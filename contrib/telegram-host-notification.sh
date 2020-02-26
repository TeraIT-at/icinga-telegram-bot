#!/bin/bash
if [ -n "$ICINGAWEB2_URL" ]; then
    HOSTDISPLAYNAME="<a href=\"$ICINGAWEB2_URL/monitoring/host/show?host=$HOSTNAME\">$HOSTDISPLAYNAME</a>"
fi
template=$(cat <<TEMPLATE
<strong>$NOTIFICATIONTYPE</strong> - $HOSTDISPLAYNAME is $HOSTSTATE

Host: $HOSTNAME
Address: $HOSTADDRESS
Date/Time: $LONGDATETIME

<pre>$HOSTOUTPUT</pre>
TEMPLATE
)
if [ -n "$NOTIFICATIONCOMMENT" ]; then
    template="$template
Comment: ($NOTIFICATIONAUTHORNAME) $NOTIFICATIONCOMMENT
"
fi

args=()
args+=(--data-urlencode "chat_id=${TELEGRAM_CHAT_ID}")
args+=(--data-urlencode "text=${template}")
args+=(--data-urlencode "parse_mode=HTML")
args+=(--data-urlencode "disable_web_page_preview=true")

echo ${NOTIFICATIONTYPE}

if ! [[ $NOTIFICATIONTYPE =~ ^(ACKNOWLEDGEMENT|RECOVERY)$ ]]; then
  if ! [[ $HOSTSTATE =~ ^(UP)$ ]]; then
    args+=(--data-urlencode 'reply_markup={"inline_keyboard":[[{"text":"Acknowledge","callback_data":"ack_host_quick"},{"text":"Acknowledge (with Comment)","callback_data":"ack_host"}]]}')
  fi
fi

if [[ $NOTIFICATIONTYPE == "ACKNOWLEDGEMENT" ]]; then
    args+=(--data-urlencode 'reply_markup={"inline_keyboard":[[{"text":"Remove Acknowledge","callback_data":"ack_host_remove"}]]}')
fi

/usr/bin/curl --silent --output /dev/null \
    "${args[@]}" \
    "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage"