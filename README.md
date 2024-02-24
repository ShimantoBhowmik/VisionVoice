# Vision Voice

## Building & Serving

### Frontend

```sh
ng serve -o
```

### Backend

Install Huggingface transformers, torch, soundfile, opencv.

```sh
uvicorn app:app --reload --host 0.0.0.0
```

