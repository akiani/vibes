// Chopin Sonata Player - Main Script
class ChopinSonataPlayer {
    constructor() {
        this.isPlaying = false;
        this.currentNoteIndex = 0;
        this.tempo = 120;
        this.notes = this.generateChopinSonata();
        this.synth = null;
        this.playbackLoop = null;
        this.startTime = 0;
        this.currentTime = 0;

        this.initAudio();
        this.initUI();
        this.renderSheetMusic();
    }

    // Generate a Chopin-style sonata with proper musical structure
    generateChopinSonata() {
        const notes = [];

        // Exposition - Theme 1 in C minor (dramatic, passionate)
        const theme1 = [
            // Measure 1-2: Opening dramatic gesture
            { pitch: 'C4', duration: '4', measure: 1 },
            { pitch: 'Eb4', duration: '4', measure: 1 },
            { pitch: 'G4', duration: '4', measure: 1 },
            { pitch: 'C5', duration: '4', measure: 1 },

            { pitch: 'B4', duration: '8', measure: 2 },
            { pitch: 'C5', duration: '8', measure: 2 },
            { pitch: 'D5', duration: '4', measure: 2 },
            { pitch: 'C5', duration: '4', measure: 2 },

            // Measure 3-4: Melodic development
            { pitch: 'Bb4', duration: '8', measure: 3 },
            { pitch: 'Ab4', duration: '8', measure: 3 },
            { pitch: 'G4', duration: '4', measure: 3 },
            { pitch: 'F4', duration: '4', measure: 3 },

            { pitch: 'Eb4', duration: '8', measure: 4 },
            { pitch: 'D4', duration: '8', measure: 4 },
            { pitch: 'C4', duration: '2', measure: 4 },
        ];

        // Bridge passage with chromatic movement
        const bridge = [
            // Measure 5-6: Transition
            { pitch: 'E4', duration: '8', measure: 5 },
            { pitch: 'F4', duration: '8', measure: 5 },
            { pitch: 'G4', duration: '8', measure: 5 },
            { pitch: 'Ab4', duration: '8', measure: 5 },

            { pitch: 'Bb4', duration: '8', measure: 6 },
            { pitch: 'C5', duration: '8', measure: 6 },
            { pitch: 'D5', duration: '4', measure: 6 },
            { pitch: 'Eb5', duration: '4', measure: 6 },
        ];

        // Theme 2 in Eb major (lyrical, singing)
        const theme2 = [
            // Measure 7-8: Lyrical melody
            { pitch: 'G4', duration: '4', measure: 7 },
            { pitch: 'Bb4', duration: '4', measure: 7 },
            { pitch: 'Eb5', duration: '4', measure: 7 },
            { pitch: 'D5', duration: '4', measure: 7 },

            { pitch: 'C5', duration: '8', measure: 8 },
            { pitch: 'Bb4', duration: '8', measure: 8 },
            { pitch: 'Ab4', duration: '4', measure: 8 },
            { pitch: 'G4', duration: '4', measure: 8 },

            // Measure 9-10: Development
            { pitch: 'F4', duration: '8', measure: 9 },
            { pitch: 'G4', duration: '8', measure: 9 },
            { pitch: 'Ab4', duration: '8', measure: 9 },
            { pitch: 'Bb4', duration: '8', measure: 9 },

            { pitch: 'C5', duration: '4', measure: 10 },
            { pitch: 'Bb4', duration: '8', measure: 10 },
            { pitch: 'Ab4', duration: '8', measure: 10 },
            { pitch: 'G4', duration: '2', measure: 10 },
        ];

        // Development section with increased intensity
        const development = [
            // Measure 11-12: Dramatic development
            { pitch: 'C5', duration: '8', measure: 11 },
            { pitch: 'D5', duration: '8', measure: 11 },
            { pitch: 'Eb5', duration: '8', measure: 11 },
            { pitch: 'F5', duration: '8', measure: 11 },

            { pitch: 'G5', duration: '4', measure: 12 },
            { pitch: 'F5', duration: '8', measure: 12 },
            { pitch: 'Eb5', duration: '8', measure: 12 },
            { pitch: 'D5', duration: '4', measure: 12 },

            // Measure 13-14: Climax
            { pitch: 'C5', duration: '8', measure: 13 },
            { pitch: 'Bb4', duration: '8', measure: 13 },
            { pitch: 'Ab4', duration: '8', measure: 13 },
            { pitch: 'G4', duration: '8', measure: 13 },

            { pitch: 'F4', duration: '4', measure: 14 },
            { pitch: 'Eb4', duration: '4', measure: 14 },
            { pitch: 'D4', duration: '4', measure: 14 },
            { pitch: 'C4', duration: '4', measure: 14 },
        ];

        // Recapitulation - Return to Theme 1
        const recapitulation = [
            // Measure 15-16: Theme 1 returns
            { pitch: 'C4', duration: '4', measure: 15 },
            { pitch: 'Eb4', duration: '4', measure: 15 },
            { pitch: 'G4', duration: '4', measure: 15 },
            { pitch: 'C5', duration: '4', measure: 15 },

            { pitch: 'B4', duration: '8', measure: 16 },
            { pitch: 'C5', duration: '8', measure: 16 },
            { pitch: 'D5', duration: '4', measure: 16 },
            { pitch: 'Eb5', duration: '4', measure: 16 },
        ];

        // Coda - Grand finale
        const coda = [
            // Measure 17-18: Final resolution
            { pitch: 'D5', duration: '8', measure: 17 },
            { pitch: 'C5', duration: '8', measure: 17 },
            { pitch: 'Bb4', duration: '8', measure: 17 },
            { pitch: 'Ab4', duration: '8', measure: 17 },

            { pitch: 'G4', duration: '4', measure: 18 },
            { pitch: 'C4', duration: '2', measure: 18 },
            { pitch: 'C4', duration: '4', measure: 18 },
        ];

        return [
            ...theme1,
            ...bridge,
            ...theme2,
            ...development,
            ...recapitulation,
            ...coda
        ];
    }

    // Initialize Tone.js audio
    initAudio() {
        this.synth = new Tone.PolySynth(Tone.Synth, {
            oscillator: {
                type: 'triangle'
            },
            envelope: {
                attack: 0.02,
                decay: 0.2,
                sustain: 0.3,
                release: 1.5
            }
        }).toDestination();

        // Add reverb for rich piano-like sound
        const reverb = new Tone.Reverb({
            decay: 3,
            wet: 0.3
        }).toDestination();

        this.synth.connect(reverb);
    }

    // Initialize UI event listeners
    initUI() {
        document.getElementById('playBtn').addEventListener('click', () => this.play());
        document.getElementById('pauseBtn').addEventListener('click', () => this.pause());
        document.getElementById('stopBtn').addEventListener('click', () => this.stop());

        const tempoSlider = document.getElementById('tempo');
        tempoSlider.addEventListener('input', (e) => {
            this.tempo = parseInt(e.target.value);
            document.getElementById('tempoValue').textContent = this.tempo;
        });

        // Edit buttons
        document.getElementById('addNoteBtn').addEventListener('click', () => this.addNote());
        document.getElementById('deleteNoteBtn').addEventListener('click', () => this.deleteLastNote());
        document.getElementById('changeNoteBtn').addEventListener('click', () => this.showNoteSelector());
        document.getElementById('regenerateBtn').addEventListener('click', () => this.regenerateSection());
        document.getElementById('applyNoteBtn').addEventListener('click', () => this.applyNoteChange());
    }

    // Render sheet music using VexFlow
    renderSheetMusic() {
        const container = document.getElementById('sheetMusic');
        container.innerHTML = '';

        const VF = Vex.Flow;
        const div = document.createElement('div');
        container.appendChild(div);

        const renderer = new VF.Renderer(div, VF.Renderer.Backends.SVG);
        renderer.resize(1100, 500);
        const context = renderer.getContext();

        // Group notes by measure
        const measures = this.groupNotesByMeasure();
        const staveWidth = 250;
        const stavesPerLine = 4;
        let staveY = 40;

        measures.forEach((measureNotes, index) => {
            const staveX = (index % stavesPerLine) * staveWidth + 10;

            if (index % stavesPerLine === 0 && index !== 0) {
                staveY += 120;
            }

            const stave = new VF.Stave(staveX, staveY, staveWidth);

            // Add clef, key signature, and time signature to first stave
            if (index === 0) {
                stave.addClef('treble');
                stave.addKeySignature('Cm');
                stave.addTimeSignature('4/4');
            }

            stave.setContext(context).draw();

            // Create VexFlow notes
            const vfNotes = measureNotes.map(note => {
                const vfNote = new VF.StaveNote({
                    keys: [note.pitch.toLowerCase()],
                    duration: note.duration
                });

                // Add accidentals if needed
                if (note.pitch.includes('b')) {
                    vfNote.addModifier(new VF.Accidental('b'), 0);
                } else if (note.pitch.includes('#')) {
                    vfNote.addModifier(new VF.Accidental('#'), 0);
                }

                return vfNote;
            });

            if (vfNotes.length > 0) {
                const voice = new VF.Voice({ num_beats: 4, beat_value: 4 });
                voice.addTickables(vfNotes);

                new VF.Formatter()
                    .joinVoices([voice])
                    .format([voice], staveWidth - 20);

                voice.draw(context, stave);
            }
        });

        this.updateTotalTime();
    }

    // Group notes by measure
    groupNotesByMeasure() {
        const measures = [];
        let currentMeasure = 1;
        let currentMeasureNotes = [];

        this.notes.forEach(note => {
            if (note.measure === currentMeasure) {
                currentMeasureNotes.push(note);
            } else {
                measures.push(currentMeasureNotes);
                currentMeasureNotes = [note];
                currentMeasure = note.measure;
            }
        });

        if (currentMeasureNotes.length > 0) {
            measures.push(currentMeasureNotes);
        }

        return measures;
    }

    // Play the sonata
    async play() {
        await Tone.start();

        this.isPlaying = true;
        this.updateButtonStates();
        this.startTime = Tone.now();

        const beatDuration = 60 / this.tempo;

        const scheduleNote = (note, index) => {
            if (!this.isPlaying || index >= this.notes.length) {
                this.stop();
                return;
            }

            const durationMap = {
                '1': beatDuration * 4,
                '2': beatDuration * 2,
                '4': beatDuration,
                '8': beatDuration * 0.5
            };

            const duration = durationMap[note.duration] || beatDuration;

            this.synth.triggerAttackRelease(note.pitch, duration);
            this.currentNoteIndex = index;
            this.updateProgress();
            this.updateMeasureInfo(note.measure);

            this.playbackLoop = setTimeout(() => {
                scheduleNote(this.notes[index + 1], index + 1);
            }, duration * 1000);
        };

        scheduleNote(this.notes[0], 0);
    }

    // Pause playback
    pause() {
        this.isPlaying = false;
        if (this.playbackLoop) {
            clearTimeout(this.playbackLoop);
        }
        this.updateButtonStates();
    }

    // Stop playback
    stop() {
        this.isPlaying = false;
        if (this.playbackLoop) {
            clearTimeout(this.playbackLoop);
        }
        this.currentNoteIndex = 0;
        this.updateProgress();
        this.updateButtonStates();
        document.getElementById('measureInfo').textContent = 'Measure 1';
    }

    // Update button states
    updateButtonStates() {
        document.getElementById('playBtn').disabled = this.isPlaying;
        document.getElementById('pauseBtn').disabled = !this.isPlaying;
        document.getElementById('stopBtn').disabled = !this.isPlaying;
    }

    // Update progress bar
    updateProgress() {
        const progress = (this.currentNoteIndex / this.notes.length) * 100;
        document.getElementById('progressFill').style.width = `${progress}%`;

        const currentSeconds = Math.floor(this.currentNoteIndex * (60 / this.tempo) * 0.5);
        const minutes = Math.floor(currentSeconds / 60);
        const seconds = currentSeconds % 60;
        document.getElementById('currentTime').textContent =
            `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }

    // Update total time
    updateTotalTime() {
        const totalSeconds = Math.floor(this.notes.length * (60 / this.tempo) * 0.5);
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        document.getElementById('totalTime').textContent =
            `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }

    // Update measure info
    updateMeasureInfo(measure) {
        document.getElementById('measureInfo').textContent = `Measure ${measure}`;
    }

    // Add a new note
    addNote() {
        const lastNote = this.notes[this.notes.length - 1];
        const newMeasure = lastNote.measure;

        const newNote = {
            pitch: 'C5',
            duration: '4',
            measure: newMeasure
        };

        this.notes.push(newNote);
        this.renderSheetMusic();
        alert('Note added! You can now change its pitch using the "Change Pitch" button.');
    }

    // Delete last note
    deleteLastNote() {
        if (this.notes.length > 1) {
            this.notes.pop();
            this.renderSheetMusic();
            alert('Last note deleted!');
        } else {
            alert('Cannot delete the last note!');
        }
    }

    // Show note selector
    showNoteSelector() {
        const selector = document.getElementById('noteSelector');
        selector.style.display = selector.style.display === 'none' ? 'flex' : 'none';
    }

    // Apply note change
    applyNoteChange() {
        if (this.notes.length > 0) {
            const lastNote = this.notes[this.notes.length - 1];
            lastNote.pitch = document.getElementById('pitchSelect').value;
            lastNote.duration = document.getElementById('durationSelect').value;

            this.renderSheetMusic();
            document.getElementById('noteSelector').style.display = 'none';
            alert('Note updated!');
        }
    }

    // Regenerate a section
    regenerateSection() {
        // Regenerate the last 8 notes with variation
        const numToRegenerate = Math.min(8, this.notes.length);
        const startIndex = this.notes.length - numToRegenerate;

        const pitches = ['C4', 'D4', 'Eb4', 'F4', 'G4', 'Ab4', 'Bb4', 'C5', 'D5', 'Eb5'];
        const durations = ['4', '8', '2'];

        for (let i = startIndex; i < this.notes.length; i++) {
            this.notes[i].pitch = pitches[Math.floor(Math.random() * pitches.length)];
            this.notes[i].duration = durations[Math.floor(Math.random() * durations.length)];
        }

        this.renderSheetMusic();
        alert('Section regenerated with new variations!');
    }
}

// Initialize the player when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.player = new ChopinSonataPlayer();
});
