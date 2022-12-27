#include <string>
#include <fstream>

void stretch_and_save_audio_file(const std::string& file_path, double stretch_factor) {
  // Lese die Audiodatei in einen Buffer
  std::ifstream input_file(file_path, std::ios::binary);
  std::vector<char> audio_data((std::istreambuf_iterator<char>(input_file)),
                               std::istreambuf_iterator<char>());

  // Berechne die neue Länge der Audiodatei aufgrund des Stretching-Faktors
  size_t new_size = audio_data.size() * stretch_factor;

  // Strecke die Audiodaten, indem du sie auf die neue Länge aufbläst
  audio_data.resize(new_size);

  // Schreibe die gestreckten Audiodaten zurück in die Datei
  std::ofstream output_file(file_path, std::ios::binary);
  output_file.write(audio_data.data(), audio_data.size());
}