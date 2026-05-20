import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  ScrollView,
  TouchableOpacity,
  TextInput,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Audio } from 'expo-av';
import { Colors, Spacing } from '@/constants';
import { ThemedText, ThemedView } from '@/components/ui';
import { useLanguageStore } from '@/store/languageStore';
import { chatWithLulu, generateSpeech } from '@/services/luluService';

interface Message {
  type: 'user' | 'lulu';
  text: string;
  lugares?: string[];
}

export default function LuluOnboardingScreen() {
  const router = useRouter();
  const { language, sessionId } = useLanguageStore();
  const [messages, setMessages] = useState<Message[]>([
    {
      type: 'lulu',
      text: language === 'es'
        ? '¡Oís! Bienvenido a Cali, la sucursal del cielo. Soy Lulú, tu guía turística virtual. ¿Qué te gustaría saber de mi ciudad?'
        : 'Hey! Welcome to Cali, heaven\'s branch. I\'m Lulú, your virtual tour guide. What would you like to know about my city?',
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const soundObject = useRef<Audio.Sound | null>(null);
  const scrollViewRef = useRef<ScrollView>(null);

  useEffect(() => {
    scrollViewRef.current?.scrollToEnd({ animated: true });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage: Message = { type: 'user', text: inputText };
    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await chatWithLulu(inputText, sessionId, language);
      const luluMessage: Message = {
        type: 'lulu',
        text: response.response,
        lugares: response.lugares,
      };
      setMessages(prev => [...prev, luluMessage]);

      // ❌ Comentar por ahora - tenemos problemas con TTS
      // await playLuluResponse(response.response);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [
        ...prev,
        {
          type: 'lulu',
          text: language === 'es'
            ? 'Ay parcero, no pude procesar eso. Intenta de nuevo.'
            : 'Oops, I couldn\'t process that. Try again.',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const playLuluResponse = async (text: string) => {
    try {
      setIsPlayingAudio(true);
      const audioBuffer = await generateSpeech(text);
      const base64Audio = Buffer.from(audioBuffer).toString('base64');
      const audioUri = `data:audio/mpeg;base64,${base64Audio}`;

      if (soundObject.current) {
        await soundObject.current.unloadAsync();
      }

      soundObject.current = new Audio.Sound();
      await soundObject.current.loadAsync({ uri: audioUri });
      await soundObject.current.playAsync();
    } catch (error) {
      console.error('Error playing audio:', error);
    } finally {
      setIsPlayingAudio(false);
    }
  };

  const handleContinue = () => {
    router.push('/onboarding/welcome');
  };

  return (
    <ThemedView variant="surface" style={{ flex: 1 }}>
      {/* Header con logo de Lulú */}
      <View
        style={{
          paddingHorizontal: Spacing.lg,
          paddingTop: Spacing.lg,
          borderBottomWidth: 1,
          borderBottomColor: Colors['surface-container'],
        }}
      >
        <ThemedText
          variant="titleLG"
          style={{ marginBottom: Spacing.md, color: Colors.primary }}
        >
          💬 Hola, soy Lulú
        </ThemedText>
      </View>

      {/* Chat */}
      <ScrollView
        ref={scrollViewRef}
        contentContainerStyle={{
          paddingHorizontal: Spacing.lg,
          paddingVertical: Spacing.lg,
        }}
        showsVerticalScrollIndicator={false}
      >
        {messages.map((msg, idx) => (
          <View
            key={idx}
            style={{
              marginBottom: Spacing.md,
              alignItems: msg.type === 'user' ? 'flex-end' : 'flex-start',
            }}
          >
            <View
              style={{
                maxWidth: '85%',
                backgroundColor:
                  msg.type === 'user'
                    ? Colors.primary
                    : Colors['surface-container'],
                borderRadius: 12,
                paddingVertical: Spacing.md,
                paddingHorizontal: Spacing.lg,
              }}
            >
              <ThemedText
                style={{
                  color: msg.type === 'user' ? 'white' : Colors.primary,
                  lineHeight: 22,
                }}
              >
                {msg.text}
              </ThemedText>

              {/* Lugares recomendados */}
              {msg.lugares && msg.lugares.length > 0 && (
                <View style={{ marginTop: Spacing.md }}>
                  {msg.lugares.map((lugar, i) => (
                    <ThemedText
                      key={i}
                      style={{
                        fontSize: 12,
                        color: msg.type === 'user' ? 'rgba(255,255,255,0.8)' : Colors['on-surface-variant'],
                        marginTop: Spacing.sm,
                      }}
                    >
                      📍 {lugar}
                    </ThemedText>
                  ))}
                </View>
              )}
            </View>
          </View>
        ))}

        {isLoading && (
          <View style={{ alignItems: 'center', marginVertical: Spacing.md }}>
            <ActivityIndicator size="large" color={Colors.primary} />
          </View>
        )}
      </ScrollView>

      {/* Input */}
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={{
          paddingHorizontal: Spacing.lg,
          paddingBottom: Spacing.lg,
          borderTopWidth: 1,
          borderTopColor: Colors['surface-container'],
        }}
      >
        <View style={{ flexDirection: 'row', gap: Spacing.md, marginBottom: Spacing.md }}>
          <TextInput
            style={{
              flex: 1,
              borderWidth: 1,
              borderColor: Colors['surface-container'],
              borderRadius: 8,
              paddingHorizontal: Spacing.md,
              paddingVertical: Spacing.md,
              fontFamily: 'System',
            }}
            placeholder={language === 'es' ? 'Pregunta algo...' : 'Ask something...'}
            value={inputText}
            onChangeText={setInputText}
            editable={!isLoading}
          />
          <TouchableOpacity
            onPress={handleSendMessage}
            disabled={isLoading || !inputText.trim()}
            style={{
              backgroundColor: Colors.primary,
              borderRadius: 8,
              width: 50,
              justifyContent: 'center',
              alignItems: 'center',
              opacity: isLoading || !inputText.trim() ? 0.5 : 1,
            }}
          >
            <ThemedText style={{ fontSize: 18 }}>➤</ThemedText>
          </TouchableOpacity>
        </View>

        {/* Botón Continuar */}
        <TouchableOpacity
          onPress={handleContinue}
          style={{
            backgroundColor: Colors.secondary,
            borderRadius: 8,
            paddingVertical: Spacing.md,
            paddingHorizontal: Spacing.lg,
            justifyContent: 'center',
            alignItems: 'center',
          }}
        >
          <ThemedText
            variant="labelLG"
            style={{
              color: 'white',
              fontWeight: '600',
            }}
          >
            {language === 'es' ? 'Continuar' : 'Continue'}
          </ThemedText>
        </TouchableOpacity>
      </KeyboardAvoidingView>
    </ThemedView>
  );
}