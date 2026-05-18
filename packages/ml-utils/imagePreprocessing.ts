export class ImagePreprocessor {
  /**
   * Prepara una imagen para TensorFlow Lite
   * - Redimensiona a 224x224 (tamaño esperado por modelo)
   * - Normaliza valores [0, 255] → [-1, 1]
   */
  static preprocess(imageData: ImageData): Float32Array {
    const canvas = document.createElement('canvas');
    canvas.width = 224;
    canvas.height = 224;
    
    const ctx = canvas.getContext('2d')!;
    ctx.drawImage(imageData as any, 0, 0, 224, 224);
    
    const pixelData = ctx.getImageData(0, 0, 224, 224).data;
    const normalized = new Float32Array(224 * 224 * 3);
    
    // Normalizar y extraer canales RGB
    for (let i = 0; i < pixelData.length; i += 4) {
      normalized[i / 4] = (pixelData[i] / 127.5) - 1.0;     // R
      normalized[(i + 1) / 4] = (pixelData[i + 1] / 127.5) - 1.0; // G
      normalized[(i + 2) / 4] = (pixelData[i + 2] / 127.5) - 1.0; // B
    }
    
    return normalized;
  }
}