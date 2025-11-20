# Chopin Sonata Player

An interactive web application that generates and plays a Chopin-style piano sonata with real-time sheet music rendering and editing capabilities.

## Features

### 🎵 Music Generation
- AI-generated sonata in C minor following classical sonata form
- Exposition with two contrasting themes
- Development section with dramatic intensity
- Recapitulation and grand coda
- Authentic Chopin-style melodic patterns and harmonic progressions

### 🎹 Real-time Playback
- High-quality piano synthesis using Tone.js
- Adjustable tempo (60-180 BPM)
- Play, pause, and stop controls
- Real-time progress tracking
- Visual measure indicator

### 📝 Sheet Music Rendering
- Professional sheet music notation using VexFlow
- Multiple measures displayed on staves
- Proper clef, key signature (C minor), and time signature (4/4)
- Automatic accidental rendering
- Scrollable music display

### ✏️ Interactive Editing
- **Add Note**: Append new notes to the composition
- **Delete Note**: Remove the last note
- **Change Pitch**: Modify note pitch (C4-C5) and duration (whole, half, quarter, eighth)
- **Regenerate Section**: Generate variations for the last 8 notes

## How to Use

1. **Open the Application**
   - Simply open `index.html` in a modern web browser
   - No server or installation required!

2. **Play the Sonata**
   - Click the "Play" button to start playback
   - Adjust tempo using the slider
   - Watch the progress bar and measure indicator

3. **Edit the Music**
   - Use the editing controls to modify the composition
   - Add or delete notes
   - Change pitch and duration of notes
   - Regenerate sections for variety

4. **Experiment**
   - Try different tempos to hear how the music changes
   - Edit the composition to create your own variations
   - Regenerate sections multiple times for different interpretations

## Technical Details

### Technologies Used
- **VexFlow 4.2.3**: Professional music notation rendering
- **Tone.js 14.8.49**: Web Audio API synthesis and scheduling
- **Vanilla JavaScript**: No framework dependencies
- **CSS3**: Modern, responsive design

### Musical Structure
- **Key**: C minor
- **Time Signature**: 4/4
- **Form**: Sonata-Allegro form
- **Style**: Romantic period, Chopin-inspired

### Browser Requirements
- Modern browser with Web Audio API support (Chrome, Firefox, Safari, Edge)
- JavaScript enabled

## Files

- `index.html` - Main HTML structure
- `style.css` - Styling and layout
- `script.js` - Music generation, playback, and editing logic
- `README.md` - This documentation

## Future Enhancements

Potential features to add:
- Save/load compositions
- Export to MIDI file
- Multiple instrument sounds
- Chord accompaniment
- More complex editing (insert notes at specific positions)
- Visual keyboard display
- Recording functionality

## Credits

Created with love for classical music and web technology!
