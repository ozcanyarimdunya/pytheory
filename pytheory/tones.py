from ._statics import REFERENCE_A, TEMPERAMENTS

class Tone:
    # __slots__ = ("name", "octave", "system")

    def __init__(self, *, name, octave=None, system='western'):
        self.name = name
        self.octave = octave

        if isinstance(system, str):
            self.system_name = system
            self._system = None
        else:
            self.system_name = None
            self._system = system

    @property
    def exists(self):
        return self.name in self.system.tones

    @property
    def system(self):
        from .systems import SYSTEMS

        if self._system:
            return self._system

        if self.system_name:
            return SYSTEMS[self.system_name]

    @property
    def full_name(self):
        if self.octave:
            return f"{self.name}{self.octave}"
        else:
            return self.name

    def __repr__(self):
        return f"<Tone {self.full_name}>"

    def __eq__(self, other):

        # Comparing string literals.
        if self.name == other:
            return True

        # Comparing against other Tones.
        try:
            if (self.name == other.name) and (self.octave == other.octave):
                return True
        except AttributeError:
            pass

    @classmethod
    def from_string(klass, s, system=None):
        tone = "".join([c for c in filter(str.isalpha, s)])
        try:
            octave = int("".join([c for c in filter(str.isdigit, s)]))
        except ValueError:
            octave = None

        if system:
            return klass(name=tone, octave=octave, system=system)
        else:
            return klass(name=tone, octave=octave)

    @classmethod
    def from_index(klass, i, *, octave, system):
        tone = system.tones[i].name
        return klass(name=tone, octave=octave, system=system)

    @property
    def _index(self):
        try:
            return self.system.tones.index(self.name)
        except AttributeError:
            raise ValueError("Tone index cannot be referenced without a system!")

    def _math(self, interval):
        """Returns (new index, new octave)."""

        octave = self.octave or 0

        try:
            mod = len(self.system.tones)
        except AttributeError:
            raise ValueError(
                "Tone math can only be computed with an associated system!"
            )
        result = self._index + interval
        index = result % mod
        octave = result // mod + octave
        return (index, octave)

    def add(self, interval):
        index, octave = self._math(interval)
        return self.from_index(index, octave=octave, system=self.system)

    def subtract(self, interval):
        return self.add((-1 * interval))

    def pitch(
        self,
        *,
        reference_pitch=REFERENCE_A,
        temperament="equal",
        symbolic=False,
        precision=None,
    ):
        try:
            tones = len(self.system.tones)
        except AttributeError:
            raise ValueError("Pitches can only be computed with an associated system!")
        pitch_scale = TEMPERAMENTS[temperament](tones)
        pitch = pitch_scale[self._index]
        if symbolic:
            return reference_pitch * pitch
        else:
            return reference_pitch * pitch.evalf(precision)
