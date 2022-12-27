function synth() {

    const audioContext = new AudioContext();
    const oscillator = audioContext.createOscillator();
    oscillator.frequency.value = 440; // Erzeugt eine A4-Note
    oscillator.connect(audioContext.destination);
    oscillator.start();

}


