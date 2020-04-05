# Access your own datastore

To get the best out of running with Github, you'll probably want to be able to access private data stores.

Treebeard lets you submit secret files inside your project directory, and injects them into your project at runtime. This is necessary for information which should not be kept in version control.

To illustrate how this works, here is an example of how to access Google Cloud Platform.

## Example: Connect to Google Cloud Storage

When running on your laptop, you can connect to Google Cloud using your developer credentials. For running on the cloud however a service account is necessary. Here is how you connect to a storage bucket on Treebeard.

### Prerequisites

We assume you already have a Google Cloud project and GCS bucket

### 1. Create your service_account.json credentials file

Navigate to [https://console.cloud.google.com/iam-admin/serviceaccounts/create](https://console.cloud.google.com/iam-admin/serviceaccounts/create)

Provide a name for your service account

Add the _Storage Admin_ role to your service account. This will let your notebook view and edit all buckets, we encourage more granular permissions if possible.

Once the service account is created, create and download a JSON key which should look similar to this:

```json
{
  "type": "service_account",
  "project_id": "treebeard-259315",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "treebeard-example@treebeard-259315.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/treebeard-example%40treebeard-259315.iam.gserviceaccount.com"
}
```

### 2. Get the credentials working locally

Move your key file next to your notebook and name it 'service-account.json'.

The Google Cloud client libraries can be directed to your credentials by setting an environment variable.

Then `pip install google-cloud-storage`

and load your key from the credentials file like so...

```python
from google.cloud import storage
from google.oauth2 import service_account
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./service-account.json"

client = storage.Client()

[b.name for b in client.list_buckets()] # Should print your storage buckets

# See the official docs for more https://googleapis.dev/python/storage/latest/index.html
```

At this point, `treebeard run` should work. However if you are triggering runs from Github you will want to avoid pushing the credentials to your repo and will need them to be fetched from the secret store.

### 3. Push the credentials to our secret store

First, add your secret to your `treebeard.yaml` file.

```yaml
notebooks:
  - run.ipynb
secret:
  - service-account.json
```

Then run `treebeard secrets push` to submit them.

```bash
➜ treebeard secrets push
🌲 Pushing Secrets for project 63db2b28e1


  Including service-account.json
🔐  done!
```

Now you can `git push` your project without the secrets and it will still be able to connect to Google Cloud at runtime.
