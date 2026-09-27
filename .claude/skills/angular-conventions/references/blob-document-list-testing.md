# Blob document list: Vitest at service, store and component layers

## Testing (Vitest)

Mock the service, not `HttpClient` directly, at both layers.

**Service layer** — assert the real URLs and the blob→anchor mechanics
(`src/ui/src/app/shared/import/import.service.spec.ts`):

```typescript
it('GETs /import/documents?houseId={id} when a houseId is given', () => {
  service.listDocuments('house-1').subscribe();
  const req = httpMock.expectOne(`${environment.webApiUrl}import/documents?houseId=house-1`);
  expect(req.request.method).toBe('GET');
  req.flush([]);
});

it('GETs /import/documents/{id}/download as a blob and triggers an anchor download', () => {
  const blob = new Blob(['file-bytes']);
  const anchors: HTMLAnchorElement[] = [];
  vi.spyOn(document, 'createElement').mockImplementation(() => {
    const a = { href: '', download: '', click: vi.fn() } as unknown as HTMLAnchorElement;
    anchors.push(a);
    return a;
  });
  globalThis.URL.createObjectURL = vi.fn().mockReturnValue('blob:url');
  globalThis.URL.revokeObjectURL = vi.fn();

  service.downloadDocument('d1', 'Mistelbach.xlsx');

  const req = httpMock.expectOne(`${environment.webApiUrl}import/documents/d1/download`);
  expect(req.request.responseType).toBe('blob');
  req.flush(blob);

  expect(anchors[0].download).toBe('Mistelbach.xlsx');
  expect(anchors[0].click).toHaveBeenCalled();
  expect(globalThis.URL.revokeObjectURL).toHaveBeenCalledWith('blob:url');
});
```

**Store layer** — assert population and that it's independent of the wizard's busy flag
(`src/ui/src/app/store/features/with-imports.spec.ts`):

```typescript
it('calls ImportService.listDocuments and populates importDocuments', () => {
  const svc = { listDocuments: vi.fn().mockReturnValue(of(docs)) };
  const store = buildStore(svc);
  store.loadDocuments('house-1');
  TestBed.flushEffects();
  expect(svc.listDocuments).toHaveBeenCalledWith('house-1');
  expect(store.importDocuments()).toEqual(docs);
});

it('does not disturb an in-progress A1/A2 draft', () => {
  const svc = { ingestMieterliste: vi.fn().mockReturnValue(of({ Draft: draft() })), listDocuments: vi.fn().mockReturnValue(of([])) };
  const store = buildStore(svc);
  store.ingestFile(new File(['x'], 'a.xlsx'));
  TestBed.flushEffects();
  store.loadDocuments('house-1');
  TestBed.flushEffects();
  expect(store.importDraft()).not.toBeNull(); // untouched
});
```

**Component layer** — assert the list renders and the download button fires
(`src/ui/src/app/resources/components/house-edit/house-edit.component.spec.ts`):

```typescript
it('renders a row per retained document with kind badge, size, and date', () => {
  importServiceSpy.listDocuments.mockReturnValue(of([doc]));
  fixture.componentRef.setInput('id', 'h1');
  fixture.detectChanges();
  const text = fixture.nativeElement.textContent as string;
  expect(text).toContain('Mistelbach.xlsx');
  expect(text).toContain('Mieterliste');
});

it('renders a working download button that calls downloadDocument on click', () => {
  importServiceSpy.listDocuments.mockReturnValue(of([doc]));
  fixture.componentRef.setInput('id', 'h1');
  fixture.detectChanges();
  const button = fixture.nativeElement.querySelector('button[aria-label="Herunterladen"]') as HTMLButtonElement;
  button.click();
  expect(importServiceSpy.downloadDocument).toHaveBeenCalledWith('d1', 'Mistelbach.xlsx');
});
```


Back to the index: [blob-document-list](blob-document-list.md)
