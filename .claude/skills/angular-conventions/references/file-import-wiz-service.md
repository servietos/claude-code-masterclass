# ImportService: FormData upload and the three endpoints

## Service (`FormData` upload; mutations use `HttpClient`, not `httpResource`)

```ts
### Service (`FormData` upload; mutations use `HttpClient`, not `httpResource`)

@Injectable({ providedIn: 'root' })
export class ImportService {
  private http = inject(HttpClient);
  private base = inject(APP_CONFIG).webApiUrl;

  ingest(file: File, review: boolean) {
    const fd = new FormData(); fd.append('file', file);
    return this.http.post<IngestionResult>(`${this.base}/import/ingest?review=${review}`, fd);
  }
  assist(body: { Draft: ImportDraft; Messages: AssistMessage[] }) {
    return this.http.post<AssistResult>(`${this.base}/import/assist`, body);
  }
  confirm(draft: ImportDraft) {
    return this.http.post<{ Id: string }>(`${this.base}/import/confirm`, draft);
  }
}
```

Back to the index: [file-import-wiz](file-import-wiz.md)
