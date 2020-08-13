# NetBox Microsoft Teams Bot

Based on:
* [Messaging Extensions](https://docs.microsoft.com/en-us/microsoftteams/platform/messaging-extensions/what-are-messaging-extensions): a special kind of Microsoft Teams application that is support by the [Bot Framework](https://dev.botframework.com) v4.
* [Search-based](https://docs.microsoft.com/en-us/microsoftteams/platform/messaging-extensions/how-to/search-commands/define-search-command) / [Action-based](https://docs.microsoft.com/en-us/microsoftteams/platform/messaging-extensions/how-to/action-commands/define-action-command): How to
build a Search-based Messaging Extension.

## Deployment

Register a new Bot in Azure *Bot Services* (see links above for info).

Copy `manifest-sample.json` to `manifest.json` and fill out all of the `<COMMENT>` areas. Zip up the "teams_app_manifest" folder and upload as a Custom App into your Teams client.

Configure Bot with settings in `config.py` or set appropriate environmental variables.

Ensure the URL you configured in *Bot Services* is reachable and start `app.py`.
