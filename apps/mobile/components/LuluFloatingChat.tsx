import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  TouchableOpacity,
  Modal,
  ScrollView,
  TextInput,
  Animated,
  ActivityIndicator,
  Dimensions,
} from 'react-native';
import { ThemedText } from '@/components/ui';
import { Colors, Spacing } from '@/constants';
import { useLanguageStore } from '@/store/languageStore';
import { chatWithLulu } from '@/services/luluService';

interface FloatingChatProps {
  contextPlace?: string; // Nombre del lugar para contexto
  visible: boolean;
  onClose: () => void;
}

interface Message {
  type: 'user' | 'lulu';
  text: string;
}

export default function LuluFloatingChat({ contextPlace, visible, onClose }: FloatingChatProps) {
  const { language, sessionId } = useLanguageStore();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const slideAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (visible && messages.length === 0) {
      // Primer mensaje contextual
      const contextMsg = contextPlace
        ? (language === 'es'
          ? `¿Quieres saber más sobre ${contextPlace}?`
          : `Want to know more about ${contextPlace}?`)
        : (language === 'es'
          ? '¿Hay algo en lo que pueda ayudarte?'
          : 'Is there anything I can help you with?');

      setMessages([{
        type: 'lulu',
        text: contextMsg,
      }]);
    }
  }, [visible, contextPlace]);

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage: Message = { type: 'user', text: inputText };
    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const context = contextPlace ? `(Contexto: El usuario está viendo ${contextPlace}) ` : '';
      const response = await chatWithLulu(
        context + inputText,
        sessionId,
        language
      );
      setMessages(prev => [...prev, { type: 'lulu', text: response.response }]);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!visible) return null;

  return (
    <Modal
      visible={visible}
      transparent
      animationType="fade"
      onRequestClose={onClose}
    >
      <View
        style={{
          flex: 1,
          backgroundColor: 'rgba(0,0,0,0.3)',
          justifyContent: 'flex-end',
        }}
      >
        {/* Chat Container */}
        <View
          style={{
            backgroundColor: Colors.surface,
            height: isExpanded ? Dimensions.get('window').height * 0.7 : 400,
            borderTopLeftRadius: 20,
            borderTopRightRadius: 20,
            paddingTop: Spacing.md,
          }}
        >
          {/* Header */}
          <View
            style={{
              flexDirection: 'row',
              justifyContent: 'space-between',
              alignItems: 'center',
              paddingHorizontal: Spacing.lg,
              paddingBottom: Spacing.md,
              borderBottomWidth: 1,
              borderBottomColor: Colors['surface-container'],
            }}
          >
            <ThemedText variant="titleMD" style={{ color: Colors.primary }}>
              💬 Lulú
            </ThemedText>
            <TouchableOpacity onPress={onClose}>
              <ThemedText style={{ fontSize: 20 }}>✕</ThemedText>
            </TouchableOpacity>
          </View>

          {/* Messages */}
          <ScrollView
            contentContainerStyle={{
              paddingHorizontal: Spacing.lg,
              paddingVertical: Spacing.md,
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
                    maxWidth: '80%',
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
                    }}
                  >
                    {msg.text}
                  </ThemedText>
                </View>
              </View>
            ))}

            {isLoading && (
              <ActivityIndicator size="small" color={Colors.primary} />
            )}
          </ScrollView>

          {/* Input */}
          <View
            style={{
              flexDirection: 'row',
              gap: Spacing.md,
              paddingHorizontal: Spacing.lg,
              paddingVertical: Spacing.md,
              borderTopWidth: 1,
              borderTopColor: Colors['surface-container'],
            }}
          >
            <TextInput
              style={{
                flex: 1,
                borderWidth: 1,
                borderColor: Colors['surface-container'],
                borderRadius: 8,
                paddingHorizontal: Spacing.md,
                paddingVertical: Spacing.sm,
              }}
              placeholder={language === 'es' ? 'Pregunta...' : 'Ask...'}
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
                width: 44,
                justifyContent: 'center',
                alignItems: 'center',
                opacity: isLoading || !inputText.trim() ? 0.5 : 1,
              }}
            >
              <ThemedText style={{ fontSize: 16 }}>➤</ThemedText>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
}