def get_subdomain_domain_tld(url: str) -> None | str:
    # Strip the URL of any scheme (http, https) and path
    domain_part = url.split('://')[-1].split('/')[0]

    # Split the domain into its components
    domain_parts = domain_part.split('.')

    # Handle subdomain, domain, and TLD
    if len(domain_parts) >= 3:
        subdomain = '.'.join(domain_parts[:-2])
        domain = domain_parts[-2]
        tld = domain_parts[-1]
        return f"{subdomain}.{domain}.{tld}"
    elif len(domain_parts) == 2:
        return domain_part  # No subdomain, just domain and TLD

    return None  # Invalid format
