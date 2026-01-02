#!/bin/bash
# Download OSC User Guide PDFs if not already present
set -e

skill_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

version="$1"
if [ -z "${version}" ]; then
	echo -e "ERROR: Missing version argument\nUse $0 <version>"
	exit 1
fi

base_url="https://docs.redhat.com/en/documentation/openshift_sandboxed_containers/${version}/pdf"

download_pdf() {
    local slug="$1"       # URL path slug (lowercase), e.g. deploying_confidential_containers_on_bare-metal_servers
    local title="$2"      # Filename title portion (title case), e.g. Deploying_confidential_containers_on_bare-metal_servers
    local description="$3" # Human-readable name for display

    local filename="OpenShift_sandboxed_containers-${version}-${title}-en-US.pdf"
    local pdf_file="${skill_dir}/${filename}"
    local url="${base_url}/${slug}/${filename}"

    if [ -f "$pdf_file" ]; then
        local size_kb=$(($(stat -f%z "$pdf_file" 2>/dev/null || stat -c%s "$pdf_file") / 1024))
        if [ "$size_kb" -gt 1 ]; then
            echo "  [cached] ${description} (${size_kb}KB)"
            echo "$pdf_file"
            return 0
        fi
        # Remove broken downloads (< 1KB)
        rm -f "$pdf_file"
    fi

    echo "  [downloading] ${description}..."

    if command -v curl &> /dev/null; then
        curl -sL "$url" -o "$pdf_file"
    elif command -v wget &> /dev/null; then
        wget -q "$url" -O "$pdf_file"
    else
        echo "ERROR: Neither curl nor wget found. Cannot download PDFs."
        exit 1
    fi

    if [ -f "$pdf_file" ]; then
        local size_kb=$(($(stat -f%z "$pdf_file" 2>/dev/null || stat -c%s "$pdf_file") / 1024))
        if [ "$size_kb" -gt 1 ]; then
            echo "  [ok] ${description} (${size_kb}KB)"
            echo "$pdf_file"
        else
            echo "  [FAILED] ${description} - file too small (${size_kb}KB), removing"
            rm -f "$pdf_file"
            return 1
        fi
    else
        echo "  [FAILED] ${description}"
        return 1
    fi
}

# Compare versions: returns 0 if $1 >= $2
version_gte() {
    local v1_major v1_minor v2_major v2_minor
    v1_major=$(echo "$1" | cut -d. -f1)
    v1_minor=$(echo "$1" | cut -d. -f2)
    v2_major=$(echo "$2" | cut -d. -f1)
    v2_minor=$(echo "$2" | cut -d. -f2)
    if [ "$v1_major" -gt "$v2_major" ]; then return 0; fi
    if [ "$v1_major" -eq "$v2_major" ] && [ "$v1_minor" -ge "$v2_minor" ]; then return 0; fi
    return 1
}

echo "OSC ${version} User Guide PDFs"
echo "========================"
echo

if version_gte "$version" "1.12"; then
    # From 1.12+, docs are split per platform/scenario
    echo "Deploying OpenShift Sandboxed Containers:"
    download_pdf \
        "deploying_openshift_sandboxed_containers_on_bare-metal_servers" \
        "Deploying_OpenShift_sandboxed_containers_on_bare-metal_servers" \
        "OSC on bare-metal servers"
    download_pdf \
        "deploying_openshift_sandboxed_containers_on_microsoft_azure" \
        "Deploying_OpenShift_sandboxed_containers_on_Microsoft_Azure" \
        "OSC on Microsoft Azure"
    download_pdf \
        "deploying_openshift_sandboxed_containers_on_ibm_z_and_ibm_linuxone" \
        "Deploying_OpenShift_sandboxed_containers_on_IBM_Z_and_IBM_LinuxONE" \
        "OSC on IBM Z and IBM LinuxONE"
    download_pdf \
        "deploying_openshift_sandboxed_containers_on_aws" \
        "Deploying_OpenShift_sandboxed_containers_on_AWS" \
        "OSC on AWS"
    download_pdf \
        "deploying_openshift_sandboxed_containers_on_google_cloud" \
        "Deploying_OpenShift_sandboxed_containers_on_Google_Cloud" \
        "OSC on Google Cloud"

    echo
    echo "Deploying Confidential Containers:"
    download_pdf \
        "deploying_confidential_containers_on_bare-metal_servers" \
        "Deploying_confidential_containers_on_bare-metal_servers" \
        "Confidential Containers on bare-metal servers"
    download_pdf \
        "deploying_confidential_containers_on_microsoft_azure" \
        "Deploying_confidential_containers_on_Microsoft_Azure" \
        "Confidential Containers on Microsoft Azure"
    download_pdf \
        "deploying_confidential_containers_on_microsoft_azure_red_hat_openshift" \
        "Deploying_confidential_containers_on_Microsoft_Azure_Red_Hat_OpenShift" \
        "Confidential Containers on Microsoft Azure Red Hat OpenShift"
    download_pdf \
        "deploying_confidential_containers_on_ibm_z_and_ibm_linuxone_with_peer_pods" \
        "Deploying_confidential_containers_on_IBM_Z_and_IBM_LinuxONE_with_peer_pods" \
        "Confidential Containers on IBM Z and IBM LinuxONE with peer pods"
    download_pdf \
        "deploying_confidential_containers_on_ibm_z_and_ibm_linuxone_bare-metal_servers" \
        "Deploying_confidential_containers_on_IBM_Z_and_IBM_LinuxONE_bare-metal_servers" \
        "Confidential Containers on IBM Z and IBM LinuxONE bare-metal"

    echo
    echo "Deploying Red Hat Build of Trustee:"
    download_pdf \
        "deploying_red_hat_build_of_trustee_for_workloads_running_on_bare-metal_servers" \
        "Deploying_Red_Hat_build_of_Trustee_for_workloads_running_on_bare-metal_servers" \
        "Trustee for bare-metal workloads"
    download_pdf \
        "deploying_red_hat_build_of_trustee_for_workloads_running_on_bare-metal_servers_in_a_disconnected_environment" \
        "Deploying_Red_Hat_build_of_Trustee_for_workloads_running_on_bare-metal_servers_in_a_disconnected_environment" \
        "Trustee for bare-metal (disconnected)"
    download_pdf \
        "deploying_red_hat_build_of_trustee_for_workloads_running_on_microsoft_azure" \
        "Deploying_Red_Hat_build_of_Trustee_for_workloads_running_on_Microsoft_Azure" \
        "Trustee for Microsoft Azure workloads"
    download_pdf \
        "deploying_red_hat_build_of_trustee_for_workloads_running_on_ibm_z_and_ibm_linuxone" \
        "Deploying_Red_Hat_build_of_Trustee_for_workloads_running_on_IBM_Z_and_IBM_LinuxONE" \
        "Trustee for IBM Z and IBM LinuxONE workloads"

    echo
    echo "Release Notes:"
    download_pdf \
        "release_notes" \
        "Release_notes" \
        "Release notes"
else
    # 1.11 and earlier: 3 monolithic PDFs
    echo "Deploying Red Hat OpenShift Sandboxed Containers:"
    download_pdf \
        "deploying_red_hat_openshift_sandboxed_containers" \
        "Deploying_Red_Hat_OpenShift_sandboxed_containers" \
        "Deployment Guide"

    echo
    echo "Deploying Confidential Containers:"
    download_pdf \
        "deploying_confidential_containers" \
        "Deploying_confidential_containers" \
        "Confidential Containers Guide"

    echo
    echo "Deploying Red Hat Build of Trustee:"
    download_pdf \
        "deploying_red_hat_build_of_trustee" \
        "Deploying_Red_Hat_build_of_Trustee" \
        "Trustee Guide"
fi

echo
echo "Download complete. PDFs are in: ${skill_dir}"
