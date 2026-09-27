# File Upload

## File Upload

### Single File Upload

```typescript
@Component({
  template: `
    <input type="file" (change)="onFileSelected($event)" />
    
    @if (uploadProgress() !== null) {
      <progress [value]="uploadProgress()" max="100"></progress>
    }
  `,
})
export class FileUpload {
  private http = inject(HttpClient);
  
  uploadProgress = signal<number | null>(null);
  
  onFileSelected(event: Event) {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    this.http.post('/api/upload', formData, {
      reportProgress: true,
      observe: 'events',
    }).subscribe(event => {
      if (event.type === HttpEventType.UploadProgress && event.total) {
        this.uploadProgress.set(Math.round(100 * event.loaded / event.total));
      } else if (event.type === HttpEventType.Response) {
        this.uploadProgress.set(null);
        console.log('Upload complete:', event.body);
      }
    });
  }
}
```

### Multiple Files

```typescript
uploadFiles(files: FileList) {
  const formData = new FormData();
  
  for (let i = 0; i < files.length; i++) {
    formData.append('files', files[i]);
  }
  
  return this.http.post<{ urls: string[] }>('/api/upload-multiple', formData);
}
```

Back to the index: [angular-http](angular-http.md)
