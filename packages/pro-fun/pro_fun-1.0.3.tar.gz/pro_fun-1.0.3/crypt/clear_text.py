text_to_encrypt = """
server {
    listen 80;
    server_name pay.ht-telecom.ru;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name pay.ht-telecom.ru;

    ##= При перезапуске сервиса в nginx состается закешированный ip-адрес
    ##= Для удобства, когда часто перезапускаются сервисы
    resolver 127.0.0.11 valid=10s;
    set $backend_finance "backend-finance:8000";
    set $frontend "frontend";
    set $keycloak "keycloak.ht-telecom.ru:8443";
    ###===

    ssl_certificate /certs/server.crt; # Path to your SSL certificate
    ssl_certificate_key /certs/server.key; # Path to your private key

    ssl_protocols TLSv1.2 TLSv1.3; # Recommended modern TLS protocols
    ssl_ciphers HIGH:!aNULL:!MD5; # Strong cipher suite
    ssl_prefer_server_ciphers off; # Allows client to choose preferred cipher

    root /usr/share/nginx/html;
    index index.html index.htm;

    error_log stderr warn;
    access_log /dev/stdout main;

    proxy_buffering off;

    proxy_intercept_errors on;

    # Заголовки безопасности
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-Port $server_port;
    proxy_set_header X-Forwarded-Ssl on;

    proxy_cookie_path /realms/isp/ /;
    proxy_cookie_path /sso/realms/isp/ /;
    proxy_cookie_domain keycloak.green.local pay.ht-telecom.ru;

    location ^~ /sso/realms/ {
        proxy_pass https://keycloak.ht-telecom.ru:8443/;
        rewrite ^/sso/realms/(.*)$ /realms/$1 break;
    }

    location /sso/auth {
        proxy_pass https://keycloak.ht-telecom.ru:8443/realms/isp/protocol/openid-connect/auth?client_id=ispapp&response_type=code&scope=openid&redirect_uri=https://pay.ht-telecom.ru;
    }

    location /sso/token {
        proxy_pass https://keycloak.ht-telecom.ru:8443/realms/isp/protocol/openid-connect/token?client_id=ispapp;
        proxy_set_header Authorization "Basic aXNwYXBwOnE3WU94SmNwOXp4alZCbnB6d3U1aEdzT2pFaEFVYUhm=";

        proxy_set_body "$request_body&redirect_uri=https://pay.ht-telecom.ru";
        proxy_set_header Content-Type "application/x-www-form-urlencoded";
    }

    location ~ /sso/(userinfo|logout)$ {
        proxy_pass https://keycloak.ht-telecom.ru:8443/realms/isp/protocol/openid-connect/$1;
    }

    location /sso/account {
        return 301 https://pay.ht-telecom.ru/sso/realms/isp/account;
    }

    location /sso/ {
        proxy_pass https://keycloak.ht-telecom.ru:8443/;

        rewrite ^/sso/(.*)$ /$1 break;
    }

    location /api/ {
        proxy_pass http://$backend_finance;

        rewrite ^/api/(.*)$ /$1 break;
    }

    location / {
        proxy_pass http://$frontend;
        proxy_intercept_errors on;
#        try_files $uri $uri/ $uri.html  =404;
    }

    error_page 403 /403.html;
    location = /403.html {
        root /usr/share/nginx/html;
        internal;
    }

    error_page 404 /404.html;
    location = /404.html {
        root /usr/share/nginx/html;
        internal;
    }
}

"""
