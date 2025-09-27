# req_to_toml.awk — BSD/macOS-safe, no bracket escaping
{
    # Remove comments
    sub(/#.*/, "")
    # Trim leading/trailing whitespace
    gsub(/^[ \t]+|[ \t]+$/, "")
    # Skip empty lines
    if (length($0) > 0) {
        print "    \"" $0 "\","
    }
}

