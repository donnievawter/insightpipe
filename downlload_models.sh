#!/bin/bash

# 📦 Load models listed in assets/models.txt into Ollama if not already present

MODEL_LIST="assets/models.txt"

# Ensure the file exists
if [ ! -f "$MODEL_LIST" ]; then
    echo "❌ Model list not found: $MODEL_LIST"
    exit 1
fi

# Get list of already pulled models
EXISTING_MODELS=$(ollama list | awk '{print $1}' | tail -n +2)

while read -r model; do
    if echo "$EXISTING_MODELS" | grep -q "^$model$"; then
        echo "✅ $model already installed"
    else
        echo "📥 Downloading $model..."
        ollama pull "$model"
    fi
done < "$MODEL_LIST"
