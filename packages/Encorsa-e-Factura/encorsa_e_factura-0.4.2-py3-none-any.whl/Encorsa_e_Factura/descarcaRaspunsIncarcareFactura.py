#!/usr/bin/env python3
import requests
import os
from typing import Dict, Any, Tuple, Optional
   

def download_invoice_response_anaf(
    id_descarcare: str,
    extras_json_str: str,
    save_path: Optional[str] = None,
) -> Tuple[int, Dict[str, Any]]:
    """
    Download the response ZIP file from ANAF for a processed invoice.
    
    The downloaded ZIP contains two XML files:
    1. The original invoice or error details (named {id_incarcare}.xml)
    2. The electronic signature from Ministry of Finance
    
    Parameters:
        id_descarcare: Download ID obtained from stareMesaj or lista mesaje response
        extras_json_str: JSON string containing:
            {
              "env": "test" | "prod",                         # default: "test"
              "oauth": {
                  "client_id": "...",
                  "client_secret": "...",
                  "refresh_token": "...",
                  "parameters": {
                      "proxi_pt_anaf_https": "",              # optional proxy for HTTPS
                      "proxi_pt_anaf_http": ""                # optional proxy for HTTP
                  }
              },
              "timeout_seconds": 60                           # optional: default 60
            }
        save_path: Optional file path to save the ZIP file. 
                   If None, returns the raw bytes in the response dict.
                   If provided, saves to disk and returns the file path.
    
    Returns:
        Tuple of (status_code, response_dict)
        
        On success (200):
        - If save_path provided: {"saved_to": file_path, "size_bytes": int}
        - If save_path is None: {"zip_content": bytes, "size_bytes": int}
        
        On error:
        - {"error": error_message, "url": request_url}
    
    Raises:
        ValueError: If required parameters are missing or invalid
        RuntimeError: If OAuth token cannot be obtained
        IOError: If file cannot be saved to disk
    """
    import json
    
    try:
        from AnafUtils import get_token_with_refresh
    except:
        from .AnafUtils import get_token_with_refresh
    
    # 1) Validate id_descarcare
    if not id_descarcare:
        raise ValueError("id_descarcare is required")
    
    id_str = str(id_descarcare).strip()
    
    # 2) Parse extras
    try:
        extras: Dict[str, Any] = json.loads(extras_json_str)
    except Exception as exc:
        raise ValueError(f"Invalid extras_json_str: {exc}")
    
    env = (extras.get("env") or "test").lower()
    timeout_seconds = int(extras.get("timeout_seconds", 60))
    
    # 3) OAuth2: obtain access token
    oauth = extras.get("oauth") or {}
    client_id = oauth.get("client_id")
    client_secret = oauth.get("client_secret")
    refresh_token = oauth.get("refresh_token")
    token_params = oauth.get("parameters") or {}
    
    if not (client_id and client_secret and refresh_token):
        raise ValueError("extras_json_str.oauth must include client_id, client_secret, and refresh_token")
    
    access_token = get_token_with_refresh(refresh_token, client_id, client_secret, token_params)
    if not access_token:
        raise RuntimeError("Could not obtain access_token from get_token_with_refresh, token is empty!")
    
    # Configure proxy if provided
    proxies = {}
    if token_params.get("proxi_pt_anaf_https"):
        proxies["https"] = token_params["proxi_pt_anaf_https"]
    if token_params.get("proxi_pt_anaf_http"):
        proxies["http"] = token_params["proxi_pt_anaf_http"]
    
    # 4) Build URL
    base = f"https://api.anaf.ro/{'test' if env == 'test' else 'prod'}/FCTEL/rest/descarcare"
    url = f"{base}?id={id_str}"
    
    # 5) Prepare headers
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    
    # 6) Send GET request
    try:
        resp = requests.get(
            url,
            headers=headers,
            timeout=timeout_seconds,
            proxies=proxies or None,
            stream=True  # Stream for potentially large files
        )
        
        if resp.status_code != 200:
            # Try to parse error response
            try:
                return resp.status_code, resp.json()
            except Exception:
                return resp.status_code, {"error": resp.text, "url": url}
        
        # Success - got ZIP file
        zip_content = resp.content
        size_bytes = len(zip_content)
        
        if save_path:
            # Save to disk
            try:
                # Ensure directory exists
                directory = os.path.dirname(save_path)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory, exist_ok=True)
                
                with open(save_path, 'wb') as f:
                    f.write(zip_content)
                
                return resp.status_code, {
                    "saved_to": save_path,
                    "size_bytes": size_bytes
                }
            except Exception as exc:
                raise IOError(f"Failed to save ZIP file to {save_path}: {exc}")
        else:
            # Return bytes
            return resp.status_code, {
                "zip_content": zip_content,
                "size_bytes": size_bytes
            }
    
    except requests.RequestException as exc:
        return 0, {"error": str(exc), "url": url}


# Usage example
if __name__ == "__main__":
    import json
    
    extras = {
        "env": "test",
        "standard": "UBL",
        "cif": "18239095",
        "oauth": {
            "client_id": "1309747503a163b2ee37047279d37e8a7e3ee71d085ddf65",
            "client_secret": "0238adeb4847d0b06f58b258545b4d287db73db70b817e8a7e3ee71d085ddf65",
            "refresh_token": "WdHky4t4SX2aHbLZuER6BOrdOE-rpv_SRH1qvw2aE5kR-3bUY1BYVI9kzOXLRKWzV0x8u3VtQZdhUUf4KwEnsJH5-rU7xwp88zfPdSRNJun-uPJC0XF4S05dZSJysK9xTU88wH7Ms80hLLupqWw5FTxPE94hLeTOxO6YamhA77tAiJ97a2jl1D2G8lzc6QAaTDlZ9Ng-0VpeCmGjjNFPDCLl7r18uV4vnm7_ykv9Tdk5jznbw6ygg2TnozuDyw3WKdZ8egIfrBjG4CIeXiAmJmci_CNUaJoVejXOlxsgNzyohA2MVdHkwcaqFNH83d6fIS7DC-O2OB17UEXnq29PGAus3pkkFvgflM9Vc8723SEqSHdl1yM4ZegKu4hexP4QcRs3jNwbKmT4ixL8Y-f1bpXAMmnp0d7VVw9D0n8iIqrFwttp4fISuET1sfnYfyOuuRw4rDEW4_E4M2Rup89_V9nfg85LPXF1EBK3XXF6vdtpnfcX20ypHPSxu7aH8VT46Cf1f-TzQ2d5iI6EXg-7zcaKhh8EGDjIT9011s_TEGCx1GjD-LSQ1rsxlgAcy92GlfzWK3gs7XU-TT9kdg_CEIOht8KRhHPVQrH-aIL_7GJvGLpzArn0BRNtYN--wv-FcuxiYtB_cLDLdyF62SzSzqVBwQMRDzSCnFYhHW-FP0HsdPYQGpJ0As3Cz55SrN7FuZW-SB6H9vEKb5Wt2U40znL6v6W9EiUil2LzlQMxAR6wyZp_PRitJkGApQdbQb3XwqD2rDM80NLmUv25WodBYAJXfUPpVXKXxFotlaX0avBxG_yGUS4zGEKQ20cZehXUxtukqt9i_3buywrmzS7KQHsMYCQkJdq3P4BWjfZh_kZGPLY7m_RLGdSdIh9mdgYXK17eDd4_wIAw3b3jn-4Ulfyil5XZuFv5SgnnM__Tu-4CH0nA9lzr-ifAZ1ylfMu3VVRB3GGEeK1wNsqiwAffyHvLgWGUeFaJM8mHumwHn_3HP6cbIpwQu-ObVcxd1gtAZQWdQnVkF8xHWWcgxRMrbM_Cpqp_ZdnnbcddqKXMOSozrGvmwMS3A3YS7LM0R1B2QkuU0dCOhkcwY3oEZMsR-SUeu6VbN1tOI-PVLbwy1KASitWoJg6A80wGt1ArjjB2UfaZNmzAP48Sa-vFOaz_K-SOgSpqsTFUkeNJB1HudEOxzkTap5cnbp2rXws0aKFKWZaNdzlinD21fAj6q8E_XEjs5TDXfa4jY9vmpOIvb8F-DaZ8GVTvaVfMia8QsMpIbPiPVkScaejUTqB5z5vih_oVg2slW6i9wLGwcvRmcazmXfpVALJAFooexE_-0ByHelKPsLuxHVkqTLuzVS0vc6vkT4SEiJmBldTII9AxdhZuezcpiW9Eyf5BqP2Yvd8cwAvck2Wj4nNm3-gRWXi2LHwMGaow7LDOIX0YysoUj_y-FOmX9FG9QNMuClprnjK6WySEKWEb22MwowrPO3lyVcvht8_vKhkInviR1zomn14mIw7F1g",
        },
    }
    
    # Option 1: Save ZIP to disk
    status_code, response = download_invoice_response_anaf(
        "3044233810",
        json.dumps(extras),
        save_path=r"E:\ENCORSA\e-Factura-V2\e-Factura-PythonLibrary\Encorsa_e_Factura\tests\Playground\downloaded.zip"
    )
    
    if status_code == 200:
        print(f"✓ ZIP saved to: {response['saved_to']}")
        print(f"  Size: {response['size_bytes']} bytes")
    else:
        print(f"✗ Download failed: {response}")
