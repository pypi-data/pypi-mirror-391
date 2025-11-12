# API

## V1

### Models

Methods:

- <code title="post /api/v1/models/tts">client.api.v1.models.<a href="./src/djelia_sdk/resources/api/v1/models/models.py">create_speech</a>(\*\*<a href="src/djelia_sdk/types/api/v1/model_create_speech_params.py">params</a>) -> object</code>

#### Translate

Types:

```python
from djelia_sdk.types.api.v1.models import (
    TranslationLanguage,
    TranslateCreateTranslationResponse,
    TranslateListSupportedLanguagesResponse,
)
```

Methods:

- <code title="post /api/v1/models/translate">client.api.v1.models.translate.<a href="./src/djelia_sdk/resources/api/v1/models/translate.py">create_translation</a>(\*\*<a href="src/djelia_sdk/types/api/v1/models/translate_create_translation_params.py">params</a>) -> <a href="./src/djelia_sdk/types/api/v1/models/translate_create_translation_response.py">TranslateCreateTranslationResponse</a></code>
- <code title="get /api/v1/models/translate/supported-languages">client.api.v1.models.translate.<a href="./src/djelia_sdk/resources/api/v1/models/translate.py">list_supported_languages</a>() -> <a href="./src/djelia_sdk/types/api/v1/models/translate_list_supported_languages_response.py">TranslateListSupportedLanguagesResponse</a></code>

#### Transcribe

Types:

```python
from djelia_sdk.types.api.v1.models import (
    FrenchTranscriptionResponse,
    TranscriptionSegment,
    TranscribeCreateTranscriptionResponse,
    TranscribeStreamTranscriptionResponse,
)
```

Methods:

- <code title="post /api/v1/models/transcribe">client.api.v1.models.transcribe.<a href="./src/djelia_sdk/resources/api/v1/models/transcribe.py">create_transcription</a>(\*\*<a href="src/djelia_sdk/types/api/v1/models/transcribe_create_transcription_params.py">params</a>) -> <a href="./src/djelia_sdk/types/api/v1/models/transcribe_create_transcription_response.py">TranscribeCreateTranscriptionResponse</a></code>
- <code title="post /api/v1/models/transcribe/stream">client.api.v1.models.transcribe.<a href="./src/djelia_sdk/resources/api/v1/models/transcribe.py">stream_transcription</a>(\*\*<a href="src/djelia_sdk/types/api/v1/models/transcribe_stream_transcription_params.py">params</a>) -> <a href="./src/djelia_sdk/types/api/v1/models/transcribe_stream_transcription_response.py">TranscribeStreamTranscriptionResponse</a></code>
