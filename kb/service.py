
        self._firebase = False
        self.supabase = None
        self.supabase_bucket = os.environ.get("SUPABASE_BUCKET", "proposal-files")
        self._configure_supabase()
        self._configure_firebase()

    def _configure_supabase(self):
        url = os.environ.get("SUPABASE_URL", "").strip()
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        if not url or not key:
            return
        try:
            from supabase import create_client
            self.supabase = create_client(url, key)
        except Exception as exc:
            raise KBError("Supabase Storage could not be initialized. Check the URL and secret key.") from exc

    @contextmanager
        location = "uploads/" + uuid4().hex + Path(filename).suffix.lower()
        target = self._file(location) if not self._firebase else None
        target = self._file(location) if not (self._firebase or self.supabase) else None
        try:
            if self._firebase:
            if self.supabase:
                self.supabase.storage.from_(self.supabase_bucket).upload(
                    location, data, {"content-type": "application/octet-stream", "upsert": "false"}
                )
            elif self._firebase:
                blob = self.firebase_bucket.blob(location)
                target.unlink(missing_ok=True)
            if self._firebase:
            if self.supabase:
                try:
                    self.supabase.storage.from_(self.supabase_bucket).remove([location])
                except Exception:
                    pass
            elif self._firebase:
                try:
        try:
            if self.supabase:
                return self.supabase.storage.from_(self.supabase_bucket).download(doc["file_location"])
            if self._firebase:
                    raise KBError("Document no longer exists.")
                if not self._firebase:
                if not (self._firebase or self.supabase):
                    target = self._file(doc["file_location"])
                              f"Close other programs and remove {staged.name} from the uploads folder.") from exc
        if self._firebase:
        if self.supabase:
            try:
                self.supabase.storage.from_(self.supabase_bucket).remove([doc["file_location"]])
            except Exception as exc:
                raise KBError("The record was deleted, but its Supabase original could not be removed.") from exc
        elif self._firebase:
            try:
