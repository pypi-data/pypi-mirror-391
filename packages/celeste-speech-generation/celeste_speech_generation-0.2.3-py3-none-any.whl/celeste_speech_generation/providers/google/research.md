# Google Gemini Speech Generation Research

## Models

| Model | Single-Speaker | Multi-Speaker | Status |
|-------|----------------|---------------|--------|
| gemini-2.5-flash-preview-tts | ✅ | ✅ | Preview |
| gemini-2.5-pro-preview-tts | ✅ | ✅ | Preview |

**Recommendation:** Use Flash for cost-efficient applications, Pro for state-of-the-art quality on complex prompts.

## API Pattern

**Endpoint:** `POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`

**Single-speaker request:**
```json
{
  "contents": [{"parts": [{"text": "Say cheerfully: Have a wonderful day!"}]}],
  "generationConfig": {
    "responseModalities": ["AUDIO"],
    "speechConfig": {
      "voiceConfig": {
        "prebuiltVoiceConfig": {"voiceName": "Kore"}
      }
    }
  }
}
```

**Multi-speaker request:**
```json
{
  "contents": [{"parts": [{"text": "TTS the following conversation..."}]}],
  "generationConfig": {
    "responseModalities": ["AUDIO"],
    "speechConfig": {
      "multiSpeakerVoiceConfig": {
        "speakerVoiceConfigs": [
          {"speaker": "Joe", "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Kore"}}},
          {"speaker": "Jane", "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Puck"}}}
        ]
      }
    }
  }
}
```

**Response format:**
```json
{
  "candidates": [{
    "content": {
      "parts": [{
        "inlineData": {
          "mimeType": "audio/pcm",
          "data": "base64_encoded_audio..."
        }
      }]
    }
  }]
}
```

## Audio Output

| Property | Value |
|----------|-------|
| Format | PCM (16-bit signed, little-endian) |
| Sample Rate | 24kHz |
| Channels | Mono (1) |
| Encoding | Base64 in response |

## Voices

30 prebuilt voices available:

| Voice | Style | Voice | Style | Voice | Style |
|-------|-------|-------|-------|-------|-------|
| Zephyr | Bright | Puck | Upbeat | Charon | Informative |
| Kore | Firm | Fenrir | Excitable | Leda | Young |
| Orus | Barrister | Aoede | Breezy | Callirrhoe | Calm |
| Autonoe | Bright | Enceladus | Breathy | Iapetus | Clear |
| Umbriel | Casual | Algieba | Smooth | Despina | Smooth |
| Erinome | Clear | Algenib | Gravelly | Rasalgethi | Informative |
| Laomedeia | Upbeat | Achernar | Soft | Alnilam | Firm |
| Schedar | Even | Gacrux | Mature | Pulcherrima | Forthright |
| Achird | Friendly | Zubenelgenubi | Relaxed | Vindemiatrix | Gentle |
| Sadachbia | Lively | Sadaltager | Knowledgeable | Sulafat | Warm |

## Languages

24 languages with auto-detection:

| Language | Code | Language | Code |
|----------|------|----------|------|
| Arabic (Egypt) | ar-EG | German (Germany) | de-DE |
| English (US) | en-US | Spanish (US) | es-US |
| French (France) | fr-FR | Hindi (India) | hi-IN |
| Indonesian (Indonesia) | id-ID | Italian (Italy) | it-IT |
| Japanese (Japan) | ja-JP | Korean (Korea) | ko-KR |
| Portuguese (Brazil) | pt-BR | Russian (Russia) | ru-RU |
| Dutch (Netherlands) | nl-NL | Polish (Poland) | pl-PL |
| Thai (Thailand) | th-TH | Turkish (Turkey) | tr-TR |
| Vietnamese (Vietnam) | vi-VN | Romanian (Romania) | ro-RO |
| Ukrainian (Ukraine) | uk-UA | Bengali (Bangladesh) | bn-BD |
| English (India) | en-IN | Marathi (India) | mr-IN |
| Tamil (India) | ta-IN | Telugu (India) | te-IN |

## Style Control

Use natural language prompts to control style, tone, accent, and pace:

**Single-speaker:**
```
Say in a spooky whisper: "By the pricking of my thumbs..."
```

**Multi-speaker:**
```
Make Speaker1 sound tired and bored, and Speaker2 sound excited and happy:

Speaker1: So... what's on the agenda today?
Speaker2: You're never going to guess!
```

## Parameters

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `responseModalities` | array | ✅ | Must be `["AUDIO"]` |
| `voiceConfig.prebuiltVoiceConfig.voiceName` | string | ✅ | One of 30 voices |
| `multiSpeakerVoiceConfig` | object | ❌ | For multi-speaker (max 2) |

## Constraints

| Constraint | Value |
|------------|-------|
| Input modality | Text only |
| Output modality | Audio only |
| Context window | 32k tokens |
| Max speakers | 2 |
| Streaming | Not supported |

## Implementation Notes

**Request transformation:**
- Unified `prompt` → `contents[0].parts[0].text`
- `voice` parameter → `speechConfig.voiceConfig.prebuiltVoiceConfig.voiceName`
- Always set `responseModalities: ["AUDIO"]`

**Response transformation:**
- Extract base64 from `candidates[0].content.parts[0].inlineData.data`
- Decode base64 to get raw PCM bytes
- MIME type: `audio/pcm` (24kHz, 16-bit, mono)
- Convert to AudioArtifact with decoded bytes

**Usage tracking:**
- No usage fields returned in response
- Character count must be calculated from input

**Voice mapping:**
- Store 30 voices in `providers/google/voices.py`
- Map Celeste `voice` parameter to `voiceName`
- Validate against Voice.id using Choice constraint

## Celeste Integration

**Model definition:**
```python
Model(
    id="gemini-2.5-flash-preview-tts",
    provider=Provider.GOOGLE,
    display_name="Gemini 2.5 Flash TTS",
    streaming=False,
    parameter_constraints={
        SpeechGenerationParameter.VOICE: Choice(options=[v.id for v in VOICES]),
    },
)
```

**Voice definition pattern:**
```python
Voice(id="kore", provider=Provider.GOOGLE, name="Kore", languages={"en-US", ...})
```
