from melody_features.features import complebm
from melody_features.representations import Melody

the_lick = Melody(midi_data={"MIDI Sequence": "Note(start=0.0, end=1.0, pitch=62, velocity=100)Note(start=1.0, end=2.0, pitch=64, velocity=100)Note(start=2.0, end=3.0, pitch=65, velocity=100)Note(start=3.0, end=4.0, pitch=67, velocity=100)Note(start=4.0, end=5.5, pitch=64, velocity=100)Note(start=5.5, end=6.5, pitch=60, velocity=100)Note(start=6.5, end=7.5, pitch=62, velocity=100)"})
print(complebm(the_lick, method='r'))