import http
from sympy import false
import os, time, yaml, datetime
from analyzer import analyze_image
from publisher import publish
from utils import is_file_stable
from tagger import tag_image
from shutil import move, copy2, copy
import argparse
import sys
import subprocess
import rawpy
import imageio
import tempfile
import logging
from enum import Enum
import requests
class MoveOrCopy(Enum):
    MOVE = "move"
    COPY = "copy"

class insightImageObject:
    def __init__(
        self,
        original_file_path: str,
        destination_file_path: str = None,
        move_or_copy: MoveOrCopy = MoveOrCopy.COPY,
        vision_friendly_path: str = None,
        generated_metadata: dict = None
    ):
        self.original_file_path = original_file_path
        self.destination_file_path = destination_file_path
        self.vision_friendly_path = vision_friendly_path
        self.move_or_copy = move_or_copy
        self.generated_metadata = generated_metadata or {
            "model_used": None,
            "description": None,
            "keywords": []
        }

    def is_raw(self) -> bool:
        raw_exts = [".orf", ".cr2", ".nef", ".arw", ".dng", ".cr3"]
        return any(self.original_file_path.lower().endswith(ext) for ext in raw_exts)

# ...existing code...
# Set up basic logging to a file
log_file = os.environ.get('INSIGHTPIPE_LOGFILE', '/tmp/insightpipenew.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger("insightpipe")

_config = {}
_model = None
_keyword_prompt = None
_ollama_url_base = None
_initialized = False
_allowed_image_types = []
def init_from_file(config_path="config.yaml"):
    global _config, _model, _keyword_prompt, _ollama_url_base, _initialized, _default_model,_prompt_source
    global _rag_api_url, _rag_k_default, _rag_enabled_default
    # Resolve config path relative to this script's directory
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), config_path)
    with open(config_path, "r") as f:
        _config = yaml.safe_load(f)
    _model = _config.get("model_name")
    _prompt_source = _config.get("prompt_source")
    _prompt_source= os.path.join(os.path.dirname(os.path.abspath(__file__)), _prompt_source)
    _keyword_prompt = _config.get("keywordPrompt")
    _ollama_url_base = _config.get("ollama_url_base")
    _default_model = _config.get("default_model","qwen2.5vl:latest")
    _initialized = True
    global _allowed_image_types
    _allowed_image_types = _config.get("allowed_image_types", ["orf", "cr","jpg"])
    _rag_api_url = _config.get("rag_api_url","http://localhost:8001")    # URL of the repo RAG API
    _rag_k_default = _config.get("rag_k_default", 5)
    _rag_enabled_default = _config.get("rag_enabled_default", False)

def parse_enum(enum_class, value, default=None):
    try:
        return enum_class(value.lower())
    except ValueError:
        return default or enum_class.COPY  # or enum_class(default)

def get_ollama_url(endpoint="chat"):
    
    return f"{_ollama_url_base.rstrip('/')}/api/{endpoint}"

def load_prompt(file_path, key):
    prompts = {}
    with open(file_path, "r") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                prompts[k.strip()] = v.strip()
    return prompts.get(key, "")



def convert_raw_to_jpg(raw_path):
    with rawpy.imread(raw_path) as raw:
        rgb = raw.postprocess()

    tmp_dir = os.path.join(tempfile.gettempdir(), "insightpipe_previews")
    os.makedirs(tmp_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(raw_path))[0] + ".jpg"
    jpg_path = os.path.join(tmp_dir, base_name)

    imageio.imwrite(jpg_path, rgb, format='JPEG')
    return jpg_path

def get_available_models():
    try:
        url = get_ollama_url("tags")
        print(f"Fetching available models from: {url}")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(f"Received model data: {data}")
        models = [model["name"] for model in data.get("models", [])]
        return models
    except requests.RequestException as e:
        print(f"[ERROR] Failed to retrieve models: {e}")
        logger.error(f"Failed to retrieve models: {e}")
        return []
def getVisionModels():
    models = sorted(get_available_models(), key=lambda x: x.lower())
    try:
      
            if _default_model in models:
                return models, _default_model
    except Exception:
        pass
    return models, None

def generate_tag_json(fpath, desc, model, timestamp, prompt, use_keywords,max_keywords=None):
    tags = {
        "filepath": fpath,
        "timestamp": timestamp,
        "model": model,
        "keywords": []
        
    }

    if use_keywords:
        raw_keywords = [kw.strip() for kw in desc.split(",")]
        if max_keywords and isinstance(max_keywords, int):
            raw_keywords = raw_keywords[:max_keywords]
        tags["keywords"] = raw_keywords
    else:
        tags["description"] = desc

    return tags

def keyword_file(fpath, model=None,max_keywords=None,job_id=None):
    global _initialized

    if not _initialized:
        init_from_file()
    source_path = fpath
    target_path = source_path
    if any(source_path.lower().endswith(f".{ext.lower()}") for ext in (_allowed_image_types or [])):
        logger.info(f"Converting RAW to JPG: {source_path}")
        target_path = convert_raw_to_jpg(source_path)
        logger.info(f"Converted to: {target_path}")


    selected_model = model if model else _model
    available_models, preselected= getVisionModels()
    if selected_model not in available_models:
        raise ValueError(f"🚫 Model '{selected_model}' not available. Choose from: {available_models}")
    ollama_url = get_ollama_url("generate")  # Use centralized method
    timestamp = datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S")
    theprompt=system_prompt + "\n" + keyword_prompt
    desc , return_job_id = analyze_image(target_path, selected_model, ollama_url, theprompt, job_id=job_id)
    if source_path != target_path and os.path.exists(target_path):
        os.remove(target_path)

    if job_id is not None:
        return generate_tag_json(fpath, desc, selected_model, timestamp, theprompt, True,max_keywords), return_job_id
    return generate_tag_json(fpath, desc, selected_model, timestamp, theprompt, True,max_keywords)    

def describe_file(fpath, prompt, model=None,job_id=None):
    source_path = fpath
    target_path = source_path
    if any(source_path.lower().endswith(f".{ext.lower()}") for ext in (_allowed_image_types or [])):
        print(f"Converting RAW to JPG: {source_path}")
        target_path = convert_raw_to_jpg(source_path)
        print(f"Converted to: {target_path}")
      
     

    timestamp = datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S")

    if not _initialized:
        init_from_file()

    selected_model = model if model else _model
    available_models , preselected = getVisionModels()
    if selected_model not in available_models:
        raise ValueError(f"🚫 Model '{selected_model}' not available. Choose from: {available_models}")
    ollama_url = get_ollama_url("generate")  # Use centralized method
    theprompt=system_prompt + "\n" + description_prompt 
    desc,return_job_id = analyze_image(target_path, selected_model, ollama_url, theprompt, job_id=job_id)
    if source_path != target_path and os.path.exists(target_path):
        os.remove(target_path)

   
    if job_id is not None:
        return {
            "filepath": fpath,
            "timestamp": timestamp,
            "model": selected_model,
            "description": desc.strip()
        }, return_job_id
    return {
        "filepath": fpath,
        "timestamp": timestamp,
        "model": selected_model,
        "description": desc.strip()
    }



def run_main_pipeline():
    from publisher import test_mqtt_connection

    # Parse CLI arguments
    parser = argparse.ArgumentParser(
        description="Run InsightPipe with optional config and runtime overrides"
    )

    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    parser.add_argument("--watch_dir", help="Folder to monitor for new images")
    parser.add_argument("--model_name", help="Local Ollama model to use")
    
    parser.add_argument("--keyword_prompt", help="Prompt for keyword generation")
    parser.add_argument("--output_dir", help="Directory to save processed images")
    parser.add_argument("--output_mode", choices=["copy", "move"], help="File handling mode")
    parser.add_argument("--dry_run", action="store_true", help="Show final config and skip execution")
    parser.add_argument("--watch", action="store_true", help="Enable watch mode for continuous tagging")
    parser.add_argument("--keywords", action="store_true", help="Enable keywording mode")
    parser.add_argument("--no_keywords", action="store_true", help="Disable keywording mode")
    parser.add_argument("--batch", action="store_true", help="Distable watch, enable batch processing of existing images")
    parser.add_argument("--mqtt_topic", help="Base topic for MQTT publishing (overrides config)")
    parser.add_argument("--input", type=str, help="Path to image file for single-file mode")
    parser.add_argument("--prompts_source", type=str, help="Path to prompts file")
    args = parser.parse_args()

    # Load config from file
    with open(args.config) as f:
        config = yaml.safe_load(f)
    global _ollama_url_base
    _ollama_url_base = config.get("ollama_url_base")
    global _allowed_image_types
    _allowed_image_types = config.get("allowed_image_types")
    ollama_url= get_ollama_url("generate")
    # Override with CLI args if provided
    if args.watch_dir:
        config["watch_dir"] = args.watch_dir
    if args.model_name:
        config["model_name"] = args.model_name
   
    if args.output_dir:
        config["output_dir"] = args.output_dir
    if args.output_mode:
        config["output_mode"] = args.output_mode
    if args.keywords:
        config["keywords"] = True
    elif args.no_keywords:
        config["keywords"] = False
    if args.watch:
        config["watch"] = True
    if args.batch:
        config["watch"] = False
    if args.mqtt_topic:
        config["mqtt_topic"] = args.mqtt_topic
    if args.prompts_source:
        config["prompts_source"] = args.prompts_source

    if args.watch and args.batch:
        print("⚠️ Conflicting flags: both --watch and --batch passed. Defaulting to watch mode.")

    model=config["model_name"]
    global system_prompt, keyword_prompt, description_prompt
    ps=config.get("prompt_source","assets/prompts.txt")
    ps=os.path.join(os.path.dirname(os.path.abspath(__file__)), ps)
    system_prompt= load_prompt(ps, "DEFAULT_SYSTEM_PROMPT")
    keyword_prompt= load_prompt(ps, "DEFAULT_KEYWORD_PROMPT")
    description_prompt= load_prompt( ps, "DEFAULT_DESCRIPTION_PROMPT")
    logger.info(f"[PROMPT SOURCE]: {ps}")
    logger.info(f"[SYSTEM PROMPT]: {system_prompt}")
    logger.info(f"[KEYWORD PROMPT]: {keyword_prompt}")
    logger.info(f"[DESCRIPTION PROMPT]: {description_prompt}")
    logger.info(f"[WATCH DIR]: {config['watch_dir']}")
    keywords=config["keywords"]
    mqtt_topic = config.get("mqtt_topic", "insightpipe")  # Default topic if not set in config

    def validate_runtime(config, dry_run=False):
        errors = []
        warnings = []

        # Check model availability
        model_name = config.get("model_name")
        available_models ,preselected = getVisionModels()
        if dry_run:
            print("[AVAILABLE MODELS]:\n", "\n* ".join(available_models))
            if args.dry_run:
                print("\n🧪 InsightPipe Dry Run — Final Configuration:\n")
            for k, v in config.items():
                print(f"  {k}: {v}")
        

        if model_name not in available_models:
            errors.append(f"Model '{model_name}' is not available via Ollama.")

        # Check MQTT topic syntax (optional example)
        topic = config.get("mqtt_topic")
        if not topic or "/" not in topic:
            errors.append(f"MQTT topic '{topic}' is malformed or missing a slash.")

        # Test MQTT connection
        logger.info("Testing MQTT connection...")
        mqtt_success, mqtt_error = test_mqtt_connection()
        if not mqtt_success:
            warnings.append(f"MQTT connection test failed: {mqtt_error}")
            logger.warning(f"⚠️ MQTT is not available - messages will not be published")
            logger.warning(f"   Error: {mqtt_error}")
        else:
            logger.info("✅ MQTT connection verified successfully")

        # Check paths
        watch_dir = config.get("watch_dir")
        if not os.path.exists(watch_dir):
            errors.append(f"Watch directory '{watch_dir}' does not exist.")

        # Report warnings
        if warnings and not dry_run:
            print("[WARNINGS]")
            for warn in warnings:
                print(f"  ⚠️  {warn}")
            print()

        # Report and bail if errors
        if errors:
            print("[CONFIG VALIDATION ERRORS]")
            for err in errors:
                print(f"  • {err}")
            sys.exit(1)
        if dry_run:
            sys.exit(0)
        
    processed= set()  # Track processed files to avoid duplicates
    validate_runtime(config, dry_run=args.dry_run)
 

    def process_watch_dir_loop():
        print("🔄 Watch mode enabled — monitoring folder for new images")
        while True:
            process_new_files()
            time.sleep(config["poll_interval"]) # Poll interval





    def process_watch_dir_once():
        print("🧪 Batch mode — processing all images in watch folder and subfolders")
        _not_raw = ['.jpg', '.jpeg', '.png', '.tif', '.tiff']
        global _allowed_image_types
        image_extensions = list(set(_allowed_image_types or []).union(set(_not_raw)))

        
        for root, dirs, files in os.walk(config["watch_dir"]):
            for f in files:
                if any(f.lower().endswith(ext) for ext in image_extensions):
                    filepath = os.path.join(root, f)
                    process_image(filepath)

        print("✅ Batch processing complete.")
        sys.exit(0)

    def process_image(fpath):
        # Create the image object
        img_obj = insightImageObject(
            original_file_path=fpath,
            move_or_copy = parse_enum(MoveOrCopy, config.get("output_mode", "copy")),
        )
        logger.info(f"Processing file: {img_obj.original_file_path} ")
        # Convert RAW to JPEG if needed
        if img_obj.is_raw():
            logger.info(f"Converting RAW to JPG: {img_obj.original_file_path}")
            img_obj.vision_friendly_path = convert_raw_to_jpg(img_obj.original_file_path)
            logger.info(f"Converted to: {img_obj.vision_friendly_path}")
            target_path = img_obj.vision_friendly_path
        else:
            target_path = img_obj.original_file_path
        logger.info(f"Using target path for analysis: {target_path}")
        # Current timestamp for tagging
        timestamp = datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S")

        # Keyword analysis (if enabled)
        if keywords:
            prompt = system_prompt + "\n" + keyword_prompt
            descKey = analyze_image(target_path, model, get_ollama_url("generate"), prompt)
            img_obj.generated_metadata["keywords"] = [kw.strip() for kw in descKey.split(",")]
            logger.info(f"Processed for keywords: {target_path} -> {descKey}")

        # Description analysis
        prompt = system_prompt + "\n" + description_prompt
        logger.info(f"Analyzing for description with prompt: {prompt}")
        desc = analyze_image(target_path, model, get_ollama_url("generate"), prompt)
        logger.info(f"Description analysis result: {desc}")
        img_obj.generated_metadata["description"] = desc.strip()
        img_obj.generated_metadata["model_used"] = model
        logger.info(f"Processed: {target_path} -> {desc}")

        # Clean up temp JPEG if RAW was converted
        if img_obj.is_raw() and img_obj.vision_friendly_path and os.path.exists(img_obj.vision_friendly_path):
            os.remove(img_obj.vision_friendly_path)

        # Decide output directory and move/copy
        try:
            output_dir = config.get("output_dir", "").strip()
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                img_obj.destination_file_path = os.path.join(output_dir, os.path.basename(img_obj.original_file_path))
                if img_obj.move_or_copy == MoveOrCopy.MOVE:
                    move(img_obj.original_file_path, img_obj.destination_file_path)
                else:
                    copy2(img_obj.original_file_path, img_obj.destination_file_path)
            else:
                img_obj.destination_file_path = img_obj.original_file_path
        except Exception as e:
            logger.error(f"Error moving/copying file {img_obj.original_file_path}: {e}")
            img_obj.destination_file_path = img_obj.original_file_path


     
        # Tag and publish
        tag_image(img_obj.destination_file_path, img_obj.generated_metadata["description"], model, timestamp, description_prompt, False)
        try:
            publish(img_obj.destination_file_path, img_obj.generated_metadata["description"], model, description_prompt, mqtt_topic)
        except Exception as e:
            logger.error(f"Failed to publish description to MQTT: {e}")
        
        if keywords:
            tag_image(img_obj.destination_file_path, descKey, model, timestamp, keyword_prompt, True)
            # try:
            #     publish(img_obj.destination_file_path, descKey, model, keyword_prompt, mqtt_topic)
            # except Exception as e:
            #     logger.error(f"Failed to publish keywords to MQTT: {e}")
       
        processed.add(img_obj.original_file_path)
      
          
   

    def process_new_files():
        _not_raw = ['.jpg', '.jpeg', '.png', '.tif', '.tiff']
        global _allowed_image_types
        image_extensions = list(set(_allowed_image_types or []).union(set(_not_raw)))
        logger.info("Scanning watch directory for new files...")
        for fname in os.listdir(config["watch_dir"]):
            fpath = os.path.join(config["watch_dir"], fname)
            logger.info(f"Checking file: {fpath}")
           
            model = config["model_name"]
            keywords = config.get("keywords", False)
            prompt = keyword_prompt if keywords else description_prompt
            if fpath in processed or not any(fpath.lower().endswith(ext) for ext in image_extensions):
                logger.info(f"Skipping : {fpath}")
                continue
            if is_file_stable(fpath, config["stabilization_interval"]):
               process_image(fpath)
    if args.watch or config.get("watch", False):
        while True:
            process_watch_dir_loop()
    elif args.batch:
        process_watch_dir_once()
        sys.exit(0)
    elif args.input:
        process_image(args.input)
        sys.exit(0)
    else:
        print("🚨 No mode selected. Use --input, --batch, or --watch.")
        sys.exit(1)
if __name__ == "__main__":

    # your CLI argument parsing and execution goes here
    run_main_pipeline()



   
  
