# Uttera for Home Assistant

Gives Assist a voice and an ear: **text to speech** and **speech to text**
through [Uttera](https://uttera.ai), processed on our own hardware in Spain.

## Install

**HACS** → Integrations → ⋮ → *Custom repositories* → add
`https://github.com/uttera/uttera-home-assistant` as an **Integration**, then
install and restart Home Assistant.

Then *Settings → Devices & Services → Add Integration → **Uttera*** and paste
your API key. Get one free at [app.uttera.ai](https://app.uttera.ai) — no card
needed.

Uttera then appears as a speech-to-text and text-to-speech engine when you
configure an Assist pipeline.

## Why you might want it

**Your audio does not leave Spain.** It is processed on our own machines,
discarded once answered, and never used to train anything. For a microphone
that lives in your house, that tends to matter more than it does elsewhere.

**It speaks 24 languages** and the voice is selectable per call.

## What it costs

Credits from your monthly allowance, the same as the API. The free plan needs
no card and is enough to try it properly.

## Two details that are deliberate

**No dependencies.** The integration uses the HTTP session Home Assistant
already has. An integration that pulls in packages is the first thing to break
when the core updates.

**Line breaks are stripped before synthesis.** Each one inserts a pause of
about 1.3 s *and is billed*, and Assist often sends text with them.

## Licence

Apache-2.0
