#!/bin/bash
##### Check DNS Propagation #####
source ./dns_helper.sh
DOMAIN="greenpower.monster"
HOSTNAME="smtp"
SERVER_IP=$(curl -s https://api.ipify.org)
if ! check_dns_propagation "$HOSTNAME.$DOMAIN" "$SERVER_IP"; then
  echo "Cannot continue because DNS hasn't propagated the A record yet - try again later"
  exit 1
fi

##### Update System #####
if ! apt update && apt upgrade -y; then
    echo "Failed to update packages. Exiting."
fi

apt install -y postfix dovecot-core dovecot-imapd certbot python3-certbot-nginx ufw lsof rsyslog mailutils

hostnamectl set-hostname "${HOSTNAME}.${DOMAIN}"

# Update /etc/hosts
echo "Configuring /etc/hosts..."
sudo tee -a /etc/hosts <<EOF
127.0.0.1       localhost
$IP             $HOSTNAME.$DOMAIN
EOF

adduser --gecos "Noreply" --disabled-password noreply && echo "noreply:Kode1234!" | chpasswd

export DEBIAN_FRONTEND=noninteractive
echo "postfix postfix/main_mailer_type select Internet" | debconf-set-selections
echo "postfix postfix/mailname string ${HOSTNAME}.${DOMAIN}" | debconf-set-selections

touch /var/log/mail.log
touch /var/log/mail.err
chmod 640 /var/log/mail.log
chmod 640 /var/log/mail.err

echo "Configuring Postfix..."
postconf -e "myhostname = ${HOSTNAME}.${DOMAIN}"
postconf -e "mydomain = ${DOMAIN}"
postconf -e "myorigin = ${DOMAIN}"
postconf -e "mydestination = ${HOSTNAME} localhost, localhost.${DOMAIN}, ${DOMAIN}, ${HOSTNAME}.${DOMAIN}"
postconf -e "inet_interfaces = all"
postconf -e "inet_protocols = ipv4"
postconf -e "mynetworks = 127.0.0.0/8"
# shellcheck disable=SC2154
postconf -e "relay_domains = $mydomain"
postconf -e "smtpd_tls_protocols = !SSLv2, !SSLv3"  # Disable insecure protocols
postconf -e "smtpd_tls_mandatory_protocols = !SSLv2, !SSLv3"
postconf -e "smtpd_tls_auth_only = no"
postconf -e "smtpd_tls_received_header = yes"
postconf -e "smtpd_tls_ciphers = high"
postconf -e "smtpd_tls_security_level = encrypt"
postconf -e "smtpd_tls_mandatory_ciphers = high"
postconf -e "smtpd_tls_exclude_ciphers = aNULL, MD5"
postconf -e 'smtpd_tls_loglevel = 4'

echo "Configuring Dovecot for SASL..."
postconf -e "smtpd_sasl_type = dovecot"
postconf -e "smtpd_sasl_path = private/auth"
postconf -e "smtpd_sasl_local_domain = ${DOMAIN}"
postconf -e "smtpd_sasl_auth_enable = yes"
postconf -e "smtpd_recipient_restrictions = permit_sasl_authenticated, reject_unauth_destination"
postconf -e "smtpd_sender_restrictions = permit_mynetworks, permit_sasl_authenticated, reject"
postconf -e "smtpd_tls_cert_file = /etc/letsencrypt/live/${HOSTNAME}.${DOMAIN}/fullchain.pem"
postconf -e "smtpd_tls_key_file = /etc/letsencrypt/live/${HOSTNAME}.${DOMAIN}/privkey.pem"
postconf -e "smtpd_use_tls = yes"
postconf -e "debug_peer_list = localhost"

cat <<EOF > /etc/postfix/relay_domains
${DOMAIN} OK
gmail.com OK
protonmail.com OK
EOF

cat <<EOF > /etc/postfix/master.cf
submission inet n       -       y       -       -       smtpd
  -o syslog_name=postfix/submission
  -o smtpd_tls_wrappermode=yes
  -o smtpd_sasl_auth_enable=yes
  -o smtpd_tls_security_level=encrypt
  -o smtpd_recipient_restrictions=permit_sasl_authenticated,reject
EOF

echo "Configuring Dovecot... (without SSL paths initially)"
cat <<EOF > /etc/dovecot/dovecot.conf
mail_location = maildir:~/Maildir
protocols = imap
auth_mechanisms = plain login

passdb {
  driver = passwd
}

userdb {
  driver = passwd
}
EOF

cat <<EOF > /etc/dovecot/conf.d/10-master.conf
service imap-login {
   inet_listener imap {
      port = 0
   }
   inet_listener imaps {
      port = 993
      ssl = yes
   }
}
service pop3-login {
  inet_listener pop3s {
    port = 995
    ssl = yes
  }
}
service auth {
   unix_listener /var/spool/postfix/private/auth {
      mode = 0660
      user = postfix
      group = postfix
   }
}
EOF

if lsof -i :80; then
    echo "Port 80 is in use. Stopping the process using it..."
    fuser -k 80/tcp
fi


echo "Obtaining Let's Encrypt certificates using --standalone web server"
if ! certbot certonly --standalone --non-interactive --agree-tos --email ta.privat@protonmail.com -d "${HOSTNAME}.${DOMAIN}"; then
    echo "Failed to obtain Let's Encrypt certificates. Please check the logs."
    exit 1
fi

if [ ! -f /etc/letsencrypt/live/${HOSTNAME}.${DOMAIN}/fullchain.pem ] || [ ! -f /etc/letsencrypt/live/${HOSTNAME}.${DOMAIN}/privkey.pem ]; then
    echo "SSL certificate files do not exist. Please check the certificate generation step."
    exit 1
fi

OLD_CERT="/etc/ssl/certs/ssl-cert-snakeoil.pem"
OLD_KEY="/etc/ssl/private/ssl-cert-snakeoil.key"
NEW_CERT="/etc/letsencrypt/live/${HOSTNAME}.${DOMAIN}/fullchain.pem"
NEW_KEY="/etc/letsencrypt/live/${HOSTNAME}.${DOMAIN}/privkey.pem"

sudo sed -i "s|$OLD_CERT|$NEW_CERT|g" /etc/postfix/main.cf
sudo sed -i "s|$OLD_KEY|$NEW_KEY|g" /etc/postfix/main.cf

echo "Updating Dovecot configuration with SSL paths..." # CHEKC THIS!
cat <<EOF >> /etc/dovecot/dovecot.conf
ssl_cert = </etc/letsencrypt/live/${HOSTNAME}.${DOMAIN}/fullchain.pem
ssl_key = </etc/letsencrypt/live/${HOSTNAME}.${DOMAIN}/privkey.pem
EOF

cat <<EOF >> /etc/dovecot/conf.d/10-master.conf
service imap-login {
  inet_listener imaps {
    port = 993
    ssl = yes
  }
}

service pop3-login {
  inet_listener pop3s {
    port = 995
    ssl = yes
  }
}
EOF

echo "Restarting Postfix..."
if ! systemctl restart postfix; then
    echo "Failed to restart Postfix. Exiting."
fi

echo "Restarting Dovecot with new SSL configuration..."
if ! systemctl restart dovecot; then
    echo "Failed to restart Dovecot. Exiting."
fi


echo "Configuring UFW firewall rules..."
ufw allow 22/tcp  # SSH
ufw allow 25/tcp  # SMTP
ufw allow 465/tcp # SMTPS
ufw allow 587/tcp # Submission
ufw allow 993/tcp # IMAPS
ufw allow 995/tcp # POP3
if ! ufw status | grep -q "Status: active"; then
    systemctl enable ufw
    ufw enable
fi

echo "Creating user noreply@${DOMAIN}..."
#doveadm user add noreply@${DOMAIN} Kode1234!
doveadm user add noreply

mkdir -p /home/noreply/Maildir/{cur,new,tmp}
chown -R noreply:noreply /home/noreply/Maildir

mkdir -p /var/mail/noreply
chown noreply:noreply /var/mail/noreply
echo "mail_location = maildir:/var/mail/noreply" >> /etc/dovecot/conf.d/10-mail.conf

echo "Mail server setup completed successfully!"

echo "This is a test email." | mail -s "Test Email Subject" noreply@${DOMAIN}
less /var/mail/noreply
# postmap /etc/postfix/relay_domains

echo "Reloading Postfix and Dovecot..."
systemctl reload postfix
systemctl reload dovecot
echo "Creating cronjob for cert renewal"
(crontab -l 2>/dev/null; echo "0 0,12 * * * certbot renew --quiet") | crontab -
echo "Finished setting up SMTP server."
systemctl restart hypersnitch.service