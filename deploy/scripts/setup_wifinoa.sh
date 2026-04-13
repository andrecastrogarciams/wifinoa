#!/bin/bash
# Configura o service do systemd e o vhost do Nginx para o projeto Wifinoa.

cat <<EOF > /etc/systemd/system/wifinoa.service
[Unit]
Description=Gunicorn instance to serve Wi-Fi Noa
After=network.target

[Service]
User=tap
Group=www-data
WorkingDirectory=/home/tap/wifinoa
Environment="PATH=/home/tap/wifinoa/venv/bin"
ExecStart=/home/tap/wifinoa/venv/bin/gunicorn --workers 3 --bind unix:/home/tap/wifinoa/wifinoa.sock wifinoa_project.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

cat <<EOF > /etc/nginx/sites-available/wifinoa
server {
    listen 80;
    server_name wifinoa.viposa.local;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        alias /home/tap/wifinoa/staticfiles/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/tap/wifinoa/wifinoa.sock;
    }
}
EOF

ln -sf /etc/nginx/sites-available/wifinoa /etc/nginx/sites-enabled/wifinoa
systemctl daemon-reload
systemctl restart wifinoa
systemctl restart nginx
