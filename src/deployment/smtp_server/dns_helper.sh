check_dns_propagation() {
    local domain="$1"
    local expected_ip="$2"
    local max_attempts=${3:-10} # 10 attempts
    local wait_interval=${4:-60}  # 1 minutes between checks

    for ((attempt=1; attempt<=max_attempts; attempt++)); do
        current_ip=$(dig +short "$domain")

        if [[ "$current_ip" == "$expected_ip" ]]; then
            echo "DNS propagated successfully. IP is: $current_ip - continuing"
            return 0
        fi

        echo "Attempt $attempt: DNS not yet propagated. Current IP: $current_ip (Expected: $expected_ip)"

        if [[ $attempt -lt $max_attempts ]]; then
            echo "Waiting $wait_interval seconds before next check..."
            sleep $wait_interval
        fi
    done

    echo "DNS propagation failed after $max_attempts attempts"
    return 1
}