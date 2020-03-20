docker run -p 8000:8000 \
  --env PORT=8000 \
  --env GOOGLE_APPLICATION_CREDENTIALS=/tmp/keys/google_creds.json \
  -v $GOOGLE_APPLICATION_CREDENTIALS:/tmp/keys/google_creds.json:ro
  8b926f89ded4