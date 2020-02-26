#!/bin/bash
if [ -n "$ICINGAWEB2_URL" ]; then
    HOSTDISPLAYNAME="<a href=\"$ICINGAWEB2_URL/monitoring/host/show?host=$HOSTNAME\">$HOSTDISPLAYNAME</a>"
    SERVICEDISPLAYNAME="<a href=\"$ICINGAWEB2_URL/monitoring/service/show?host=$HOSTNAME&service=$SERVICEDESC\">$SERVICEDISPLAYNAME</a>"
fi
template=$(cat <<TEMPLATE
<strong>$NOTIFICATIONTYPE</strong> $HOSTDISPLAYNAME - $SERVICEDISPLAYNAME is $SERVICESTATE

Host: $HOSTNAME
Service: $SERVICEDESC
Address: $HOSTADDRESS
Date/Time: $LONGDATETIME

<pre>$SERVICEOUTPUT</pre>
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


if ! [[ $NOTIFICATIONTYPE =~ ^(ACKNOWLEDGEMENT|RECOVERY)$ ]]; then
  if ! [[ $SERVICESTATE =~ ^(OK)$ ]]; then
    args+=(--data-urlencode 'reply_markup={"inline_keyboard":[[{"text":"Acknowledge","callback_data":"ack_service_quick"},{"text":"Acknowledge (with Comment)","callback_data":"ack_service"}]]}')
  fi
fi

if [[ $NOTIFICATIONTYPE == "ACKNOWLEDGEMENT" ]]; then
    args+=(--data-urlencode 'reply_markup={"inline_keyboard":[[{"text":"Remove Acknowledge","callback_data":"ack_service_remove"}]]}')
fi


/usr/bin/curl --silent --output /dev/null \
    "${args[@]}" \
    "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage"