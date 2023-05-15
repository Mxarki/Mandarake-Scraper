Mandarake Item Notifier

This Python script monitors Mandarake's website for new items and sends notifications to Discord channels using webhooks.
Requirements

    Python 3.6 or higher
    configparser module
    datetime module
    requests module
    re module
    time module
    os module
    json module
    bs4 module

Installation

    Clone the repository or download the script.
    Install the required modules using pip.

pip install configparser requests bs4 lxml

    Configure the script by editing config.ini.
        Add the URLs to monitor in the Directory section.
        Set the desired check interval (in seconds) in the Function section.
        Set the path and name of the file to store past items in the Function section.
        Set the URLs for the log and alert webhooks in the Discord section.
        Set the Discord role ID to mention in the Discord section.
        Set the desired language for the webhook message in the Discord section.
    Run the script using the following command:

python mandarake_notifier.py

Usage

The script will continuously monitor the specified URLs for new items and send notifications to the specified Discord channel using webhooks. The script will log its actions to the console and to the log webhook.
License

This project is licensed under the MIT License - see the LICENSE.md file for details.
