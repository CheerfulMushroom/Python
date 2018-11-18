class TextHistory:

    def __init__(self, text=""):
        self._text = text
        self._version = 0
        self._changes = dict()

    @property
    def text(self):
        return self._text

    @property
    def version(self):
        return self._version

    def action(self, action):
        if not (0 <= action.from_version < action.to_version):
            raise ValueError
        self._text = action.apply(self._text)
        self._version = action.to_version
        self._changes[self._version] = action
        return self._version

    def insert(self, text, pos=None):
        if pos is None:
            pos = len(self._text)
        if not (0 <= pos <= len(self._text)):
            raise ValueError
        action = InsertAction(pos, text, from_version=self._version, to_version=self._version + 1)
        self.action(action)
        return self._version

    def replace(self, text, pos=None):
        if pos is None:
            pos = len(self._text)
        if not (0 <= pos <= len(self._text)):
            raise ValueError
        action = ReplaceAction(pos, text, from_version=self._version, to_version=self._version + 1)
        self.action(action)
        return self._version

    def delete(self, pos, length):
        if not (0 <= pos <= pos + length <= len(self._text)):
            raise ValueError
        action = DeleteAction(pos, length, from_version=self._version, to_version=self._version + 1)
        self.action(action)
        return self._version

    def get_actions(self, from_version=None, to_version=None):
        if from_version is None:
            from_version = 0
        if to_version is None:
            to_version = len(self._changes)
        if not (0 <= from_version <= to_version <= self._version):
            raise ValueError
        raw_actions = [action for version, action in self._changes.items() if from_version < version <= to_version]
        return raw_actions


class Action:
    def __init__(self, pos, from_version, to_version):
        self.pos = pos
        self.from_version = from_version
        self.to_version = to_version


class InsertAction(Action):
    def __init__(self, pos, text, from_version, to_version):
        super().__init__(pos, from_version, to_version)
        self.text = text

    def __repr__(self):
        return f'insert(text="{self.text}", pos={self.pos}, from_ver={self.from_version}, to_ver={self.to_version})'

    def apply(self, original_text):
        return "".join([original_text[:self.pos], self.text, original_text[self.pos:]])


class ReplaceAction(Action):
    def __init__(self, pos, text, from_version, to_version):
        super().__init__(pos, from_version, to_version)
        self.text = text

    def __repr__(self):
        return f'replace(text="{self.text}", pos={self.pos}, from_ver={self.from_version}, to_ver={self.to_version})'

    def apply(self, original_text):
        return "".join([original_text[:self.pos], self.text, original_text[self.pos + len(self.text):]])


class DeleteAction(Action):
    def __init__(self, pos, length, from_version, to_version):
        super().__init__(pos, from_version, to_version)
        self.length = length

    def __repr__(self):
        return f'delete(pos={self.pos}, len={self.length}, from_ver={self.from_version}, to_ver={self.to_version})'

    def apply(self, original_text):
        return "".join([original_text[:self.pos], original_text[self.pos + self.length:]])
