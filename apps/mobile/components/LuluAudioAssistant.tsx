import React, { useState, useRef } from 'react';
import {
  View,
  TouchableOpacity,
  Animated,
  ActivityIndicator,
} from 'react-native';
import { Audio } from 'expo-av';
import { Colors, Spacing } from '@/constants';
import { ThemedText } from '@/components/ui';
import { useLanguageStore } from '@/store/languageStore';
import { chatWithLulu, transcribeAudio, generateSpeech } from '@/services/luluService';

interface AudioAssistantProps {
  position?: 'bottom-right' | 'bottom-left';
  style?: any;
}

export default function LuluAudioAssistant({ position = 'bottom-right', style }: AudioAssistantProps) {
  const { language, sessionId } = useLanguageStore();
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const recordingRef = useRef<Audio.Recording | null>(null);
  const soundRef = useRef<Audio.Sound | null>(null);
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const pulseAnim = useRef(new Animated.Value(0)).current;

  // Animación de pulse cuando se está grabando
  React.useEffect(() => {
    if (isRecording) {
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 600,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 0,
            duration: 600,
            useNativeDriver: true,
          }),
        ])
      ).start();
    }
  }, [isRecording]);

  const startRecording = async () => {
    try {
      await Audio.requestPermissionsAsync();
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const recording = new Audio.Recording();
      await recording.prepareToRecordAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      await recording.startAsync();
      recordingRef.current = recording;
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
    }
  };

  const stopRecording = async () => {
    try {
      if (!recordingRef.current) return;

      await recordingRef.current.stopAndUnloadAsync();
      const uri = recordingRef.current.getURI();
      setIsRecording(false);
      setIsProcessing(true);

      // Transcribir audio
      const text = await transcribeAudio(uri || '', language);
      console.log('Transcribed:', text);

      // Enviar a Lulú
      const response = await chatWithLulu(text, sessionId, language);

      // Reproducir respuesta
      await playAudioResponse(response.response);

      setIsProcessing(false);
    } catch (error) {
      console.error('Error processing audio:', error);
      setIsProcessing(false);
    }
  };

  const playAudioResponse = async (text: string) => {
    try {
      setIsPlaying(true);
      const audioBuffer = await generateSpeech(text);
      const base64Audio = Buffer.from(audioBuffer).toString('base64');
      const audioUri = `data:audio/mpeg;base64,${base64Audio}`;

      if (soundRef.current) {
        await soundRef.current.unloadAsync();
      }

      soundRef.current = new Audio.Sound();
      await soundRef.current.loadAsync({ uri: audioUri });
      await soundRef.current.playAsync();

      // Esperar a que termine
      soundRef.current?.setOnPlaybackStatusUpdate((status: any) => {
        if (status.didJustFinish) {
          setIsPlaying(false);
        }
      });
    } catch (error) {
      console.error('Error playing audio:', error);
      setIsPlaying(false);
    }
  };

  const handlePress = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const positionStyle =
    position === 'bottom-right'
      ? { bottom: Spacing.lg, right: Spacing.lg }
      : { bottom: Spacing.lg, left: Spacing.lg };

  return (
    <View
      style={[
        {
          position: 'absolute',
          zIndex: 999,
        },
        positionStyle,
        style,
      ]}
    >
      {/* Pulse cuando está grabando */}
      {isRecording && (
        <Animated.View
          style={{
            position: 'absolute',
            width: 80,
            height: 80,
            borderRadius: 40,
            backgroundColor: Colors.primary,
            opacity: pulseAnim.interpolate({
              inputRange: [0, 1],
              outputRange: [0.3, 0],
            }),
            alignSelf: 'center',
            top: 0,
            left: 0,
          }}
        />
      )}

      {/* Botón principal */}
      <TouchableOpacity
        onPress={handlePress}
        disabled={isProcessing || isPlaying}
        style={{
          width: 70,
          height: 70,
          borderRadius: 35,
          backgroundColor:
            isRecording || isProcessing || isPlaying
              ? Colors.secondary
              : Colors.primary,
          justifyContent: 'center',
          alignItems: 'center',
          elevation: 8,
          shadowColor: Colors.primary,
          shadowOffset: { width: 0, height: 2 },
          shadowOpacity: 0.3,
          shadowRadius: 4,
          opacity:
            isProcessing || isPlaying ? 0.7 : 1,
        }}
      >
        {isProcessing ? (
          <ActivityIndicator size="large" color="white" />
        ) : isRecording ? (
          <ThemedText style={{ fontSize: 28 }}>⏹️</ThemedText>
        ) : isPlaying ? (
          <ThemedText style={{ fontSize: 28 }}>🔊</ThemedText>
        ) : (
          <ThemedText style={{ fontSize: 28 }}>🎤</ThemedText>
        )}
      </TouchableOpacity>

      {/* Label */}
      <View
        style={{
          marginTop: Spacing.md,
          paddingHorizontal: Spacing.md,
          paddingVertical: Spacing.sm,
          backgroundColor: Colors.surface,
          borderRadius: 8,
          borderWidth: 1,
          borderColor: Colors['surface-container'],
        }}
      >
        <ThemedText
          style={{
            fontSize: 12,
            color: Colors.primary,
            fontWeight: '600',
            textAlign: 'center',
          }}
        >
          {isRecording
            ? language === 'es' ? 'Grabando...' : 'Recording...'
            : isProcessing
            ? language === 'es' ? 'Procesando...' : 'Processing...'
            : isPlaying
            ? language === 'es' ? 'Reproduciendo...' : 'Playing...'
            : language === 'es' ? 'Habla aquí' : 'Speak here'}
        </ThemedText>
      </View>
    </View>
  );
}