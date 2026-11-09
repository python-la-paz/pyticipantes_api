# apitoken
To Startup configure .env using .env.production

```py
uvicorn app.main:app --host 0.0.0.0  --reload
```
## To execute using vscode
To Run project using uvicorn run:
- Python: Uvicorn -> Ctrl + F5

To Run project using uvicorn Run And Debug:
- Python: Uvicorn -> F5

In the TAB Run and Debug "Ctrl + Shift + D" can select, run all project or run single file

For Single File 
To Run project using uvicorn run:
- Python: Run Single File -> Ctrl + F5

To Run project using uvicorn Run And Debug:
- Python: Run Single File -> F5

> In both Cases, the file .vscode/launch.json load file .env to environment variables

## To run in Container Docker use
```sh
docker-compose -f docker-compose.dev.yaml up -d --build
```
## To run in Kubernetes 
First build image one form is using docker-compose
```sh
docker-compose -f docker-compose.dev.yaml build
```
Create a secret with the .env file
```sh
kubectl create secret generic apitoken --from-env-file=.env 
```
Run  de files in k8s deployment 
```sh
kubectl create -f ./k8s/deploy.yaml
```
### 1. To run in local using Port Forward
To run the service use port-forward in new terminal and **"don't close"**
```sh
kubectl port-forward deploy/apitoken 8000:8000
```
Use curl o browser to test localhost:8000

### 2. To run in local using Expose
To expose in Nodeport service use
```sh
kubectl create -f ./k8s/expose.yaml
```
Expose the endpoint using a port 30007, Kubernetes use a range in ports (30000-32767)
Use curl o browser to test localhost:3007

# Test
The unit test are in the test folder in app, for execute test using Pytest:
```sh
pytest
#For more details
pytest -v -s
```

## Event registration dates

`date` is the event date only; it no longer controls event registration.
Create and update events with `registration_start` and `registration_end`:

```json
{
    "title": "Python meetup",
    "description": "Community event",
    "date": "2026-12-05T18:00:00-04:00",
    "location": "La Paz",
    "registration_start": "2026-11-01T10:00:00-04:00",
    "registration_end": "2026-11-30T15:30:00-04:00",
    "public": true,
    "finished": false
}
```

Registration uses the exact start and end datetimes (both inclusive),
in Bolivia (UTC-04:00). The example opens at 10:00 and closes at 15:30
on their respective dates; times are never extended to the end of the day.
Offsets are converted to Bolivia time; inputs without an offset are interpreted
as Bolivia time. These two fields are stored and returned as offset-free Bolivia
local datetimes. The start must not be after the end, including when both
fall on the same day. Midnight means 00:00, not the end of that day.
To allow an entire end day, explicitly send its end time (for example 23:59:59).
Previously saved end times are not changed automatically; update existing
events and activities if they should close at a different hour.

Both fields default to `null` for compatibility with existing events. Events
missing either field remain queryable but cannot accept registrations until both
dates are configured. An update that omits them clears the registration period.
Events must still be public, enabled and not marked as finished; quota,
duplicate-registration and participant-data checks remain unchanged.

Load the three `event_registration_*` entries from `default/messages.json` into
the existing messages collection when deploying, so registration errors have
their Spanish translations.

## Activity registration dates

Activities use the same `registration_start` and `registration_end` fields and
Bolivia timezone rules as events. `date` is only the activity date and does not
control registrations. Both fields are accepted on activity creation and update,
and returned in activity responses, including activities listed under an event.

Registration uses the exact start and end datetimes (both inclusive), including
their hours, minutes and seconds. Missing either date blocks registration without
preventing activity queries. Updates that omit these fields clear the period.
Activities must still be public, enabled and not finished; quota, duplicate and
participant-data checks are unchanged. Cancellation rules are unchanged.
Each activity's registration period is independent of its event's period.

Load the three `activity_registration_*` entries from `default/messages.json`
into the existing messages collection when deploying, and configure both dates
on existing activities before accepting registrations.

## Typed additional information

Event and activity `additional_info` contains ordered question objects:

```json
{
    "additional_info": [
        {"question": "Select your favorite IDEs", "type": "multiple", "options": ["vscode", "atom"]},
        {"question": "Do you agree to these terms?", "type": "single", "options": ["yes", "no"]},
        {"question": "What is your pet's name?", "type": "text"}
    ]
}
```

Types are `text`, `single`, and `multiple`. Choice questions require unique,
non-empty options; text questions cannot have options. Legacy plain-string
questions are read as `text` questions and returned as question objects.
Existing registration answers remain readable.

For both public registration endpoints, send one multipart/form-data field
named `additional_info` containing a JSON-encoded answer array, or repeated
`additional_info` fields containing JSON question/answer objects.
The file upload and other form fields are unchanged.
For example, the field value for these questions is:

```json
[["vscode", "atom"], "yes", "Luna"]
```

Alternatively, send each of the following JSON objects as a separate
`additional_info` field, in question order (a single JSON array of these objects
is also accepted):

```json
{"question": "Select your favorite IDEs", "type": "multiple", "answer": ["vscode", "atom"]}
{"question": "Do you agree to these terms?", "type": "single", "answer": "yes"}
{"question": "What is your pet's name?", "type": "text", "answer": "Luna"}
```

The objects' `answer` values are extracted before registration validation and
storage; submitted labels do not replace the configured questions or options.

Answers match questions by position: `text` and `single` use strings, and
`multiple` uses an array of selected option strings. Every question requires
a non-empty answer. Unknown options, duplicate selections, incorrect answer
types, and missing or extra answers are rejected before uploading documents.
Omitting the field means `[]`, valid only when there are no questions.
Registrations store and return this mixed array without converting selections
to strings. Clients must update question rendering and JSON-encode either the
entire answer array or each question/answer object when submitting registrations.

## Registration email notifications

Set `SMTP_HOST`, `SMTP_PORT`, `SMTP_FROM`, `SMTP_USERNAME`, `SMTP_PASSWORD`,
`SMTP_SECURITY` and `SMTP_TIMEOUT` in the deployment environment. See
`.env.production` for placeholder values; provide real credentials through a
secret manager or environment variables, not in the repository. Security can be
`starttls` (normally port 587) or `ssl` (normally port 465). Authentication is
optional, but if used both username and password must be set.

Administrators can use OpenAPI to configure HTML notifications with
`PUT /api/event/{id}/email-config` and `PUT /api/activity/{id}/email-config`.
The corresponding `GET` endpoints return the saved configuration:

```json
{
  "email_enabled": true,
  "email_template": "<p>Hola {{given_name}}, recibimos tu registro como {{username}}.</p>"
}
```

The permitted user placeholders are `{{username}}`, `{{given_name}}`,
`{{family_name}}` and `{{email}}`. Optional user values become empty strings;
values are escaped before inserting them into HTML. Unknown placeholders are
rejected. The template is required when the flag is true. Set
`email_enabled` to false to disable sending; existing records default to false.
These settings are managed separately from the normal event/activity update
endpoints and are not exposed in public event/activity responses.

One email is attempted after a registration is saved, whether its status is
pending or accepted. An SMTP error does not undo the registration or cause a
duplicate on retry; it is logged with the registration ID and is not retried
automatically. Registration success does not guarantee email delivery. Configure
log monitoring and check SMTP settings before enabling notifications.

### Email attempt log

Every attempt is stored in the `email_log` collection with `date` (UTC),
`email`, `user`, `username`, `item_type` (`event` or `activity`), `event`,
`activity`, `registration`, `subject`, the rendered HTML `template`, `success`
and `error`. Activity attempts also store their parent `event`. Nothing is
logged when `email_enabled` is false. Failures before rendering (for example,
missing configuration) are logged with `template` set to `null`.

Review attempts with `GET /api/event/{id}/email-logs` (includes the event's
activities) or `GET /api/activity/{id}/email-logs`. Use `success=false` to find
failed sends; `page_number` and `n_per_page` paginate the results. Compare the
registrations with the logged attempts to confirm every registrant was emailed.


# Emain into Json Payload

```python
import json

html = """
    <p>Hola {{given_name}}, recibimos tu registro como {{username}}.</p>
"""

payload = {
    "email_enabled": True,
    "email_template": html
}

json_string = json.dumps(payload, ensure_ascii=False)

print(json_string)
```
