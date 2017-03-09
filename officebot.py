import os
import time
import re
import random
import configparser
from slackclient import SlackClient
from patterns import pairs


config = configparser.ConfigParser()
config.read('config.ini')


def handle_command(command, channel):
    """Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification."""

    response = "Sure...write some more code then I can do that!"

    for pair in pairs:
        if re.compile(pair[0]).match(command):
            response = random.choice(pair[1])
            break

    slack_client.api_call("chat.postMessage", channel=channel,
            text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID."""

    AT_BOT = "<@" + config['SLACK']['BOT_ID'] + ">"
    output_list = slack_rtm_output

    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                        output['channel']

    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1

    slack_client = SlackClient(config['SLACK']['BOT_TOKEN'])

    if slack_client.rtm_connect():

        print('PersonalBot connected and running!')

        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())

            if command and channel:
                handle_command(command, channel)

            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print('Connection failed. Invalid Slack token or bot ID?')
