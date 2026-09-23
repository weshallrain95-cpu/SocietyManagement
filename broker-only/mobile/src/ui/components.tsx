import React from 'react';
import {
  ActivityIndicator, Pressable, RefreshControl, ScrollView, StyleSheet, Text, TextInput, View,
  type TextInputProps, type ViewStyle,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { font, radius, space, usePalette, type Palette } from './theme';

export function Screen({ children, onRefresh, refreshing = false, scroll = true }: {
  children: React.ReactNode; onRefresh?: () => void; refreshing?: boolean; scroll?: boolean;
}) {
  const c = usePalette();
  const body = scroll ? (
    <ScrollView
      contentContainerStyle={{ padding: space.lg, gap: space.md, paddingBottom: 48 }}
      keyboardShouldPersistTaps="handled"
      refreshControl={onRefresh ? <RefreshControl refreshing={refreshing} onRefresh={onRefresh} /> : undefined}
    >
      {children}
    </ScrollView>
  ) : (
    <View style={{ flex: 1, padding: space.lg, gap: space.md }}>{children}</View>
  );
  return <SafeAreaView edges={['bottom']} style={{ flex: 1, backgroundColor: c.bg }}>{body}</SafeAreaView>;
}

export function H1({ children }: { children: React.ReactNode }) {
  const c = usePalette();
  return <Text style={{ fontSize: font.big, fontWeight: '700', color: c.text }}>{children}</Text>;
}

export function H2({ children, right }: { children: React.ReactNode; right?: React.ReactNode }) {
  const c = usePalette();
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginTop: space.sm }}>
      <Text style={{ fontSize: font.title - 3, fontWeight: '700', color: c.text }}>{children}</Text>
      {right}
    </View>
  );
}

export function P({ children, muted, small, style }: { children: React.ReactNode; muted?: boolean; small?: boolean; style?: object }) {
  const c = usePalette();
  return <Text style={[{ fontSize: small ? font.small : font.body, color: muted ? c.textMuted : c.text, lineHeight: small ? 18 : 21 }, style]}>{children}</Text>;
}

export function Card({ children, onPress, style, testID }: { children: React.ReactNode; onPress?: () => void; style?: ViewStyle; testID?: string }) {
  const c = usePalette();
  const base: ViewStyle = { backgroundColor: c.surface, borderRadius: radius.md, borderWidth: 1, borderColor: c.border, padding: space.md, gap: space.xs };
  if (!onPress) return <View style={[base, style]} testID={testID}>{children}</View>;
  return (
    <Pressable onPress={onPress} testID={testID} accessibilityRole="button" style={({ pressed }) => [base, style, pressed && { opacity: 0.7 }]}>
      {children}
    </Pressable>
  );
}

type ButtonKind = 'primary' | 'secondary' | 'ghost' | 'danger';
export function Button({ title, onPress, kind = 'primary', disabled, busy, small, testID }: {
  title: string; onPress: () => void; kind?: ButtonKind; disabled?: boolean; busy?: boolean; small?: boolean; testID?: string;
}) {
  const c = usePalette();
  const bg = { primary: c.brand, secondary: c.surfaceAlt, ghost: 'transparent', danger: c.badBg }[kind];
  const fg = { primary: c.brandText, secondary: c.text, ghost: c.brand, danger: c.bad }[kind];
  return (
    <Pressable
      testID={testID}
      accessibilityRole="button"
      accessibilityState={{ disabled: disabled || busy }}
      disabled={disabled || busy}
      onPress={onPress}
      style={({ pressed }) => ({
        backgroundColor: bg, borderRadius: radius.md, minHeight: small ? 36 : 48, paddingHorizontal: small ? space.md : space.lg,
        alignItems: 'center', justifyContent: 'center', opacity: disabled ? 0.45 : pressed ? 0.75 : 1,
        borderWidth: kind === 'secondary' ? 1 : 0, borderColor: c.border,
      })}
    >
      {busy ? <ActivityIndicator color={fg} /> : <Text style={{ color: fg, fontWeight: '600', fontSize: small ? font.small : font.body }}>{title}</Text>}
    </Pressable>
  );
}

export function Field({ label, hint, error, ...props }: TextInputProps & { label: string; hint?: string; error?: string }) {
  const c = usePalette();
  return (
    <View style={{ gap: space.xs }}>
      <Text style={{ color: c.text, fontWeight: '600', fontSize: font.small }}>{label}</Text>
      <TextInput
        placeholderTextColor={c.textMuted}
        {...props}
        style={{
          backgroundColor: c.surface, borderRadius: radius.sm, borderWidth: 1, borderColor: error ? c.bad : c.border,
          paddingHorizontal: space.md, minHeight: 48, fontSize: font.body, color: c.text,
        }}
      />
      {error ? <P small style={{ color: c.bad }}>{error}</P> : hint ? <P small muted>{hint}</P> : null}
    </View>
  );
}

export function Chip({ label, selected, onPress, tone }: { label: string; selected?: boolean; onPress?: () => void; tone?: 'ok' | 'bad' | 'warn' | 'info' }) {
  const c = usePalette();
  const toneBg = tone ? { ok: c.okBg, bad: c.badBg, warn: c.warnBg, info: c.infoBg }[tone] : undefined;
  const toneFg = tone ? { ok: c.ok, bad: c.bad, warn: c.warn, info: c.info }[tone] : undefined;
  return (
    <Pressable
      onPress={onPress}
      disabled={!onPress}
      accessibilityRole={onPress ? 'button' : 'text'}
      accessibilityState={{ selected }}
      style={{
        paddingHorizontal: space.md, paddingVertical: 7, borderRadius: radius.pill, borderWidth: 1,
        borderColor: selected ? c.brand : toneBg ? 'transparent' : c.border,
        backgroundColor: selected ? c.brand : toneBg ?? c.surface, minHeight: 34, justifyContent: 'center', alignSelf: 'flex-start',
      }}
    >
      <Text style={{ color: selected ? c.brandText : toneFg ?? c.text, fontSize: font.small, fontWeight: selected ? '600' : '500' }}>{label}</Text>
    </Pressable>
  );
}

export function ChipRow({ children }: { children: React.ReactNode }) {
  return <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: space.sm }}>{children}</View>;
}

export function Choice<T extends string>({ label, options, value, onChange }: {
  label?: string; options: { value: T; label: string }[]; value: T | undefined; onChange: (v: T) => void;
}) {
  return (
    <View style={{ gap: space.xs }}>
      {label ? <P small style={{ fontWeight: '600' }}>{label}</P> : null}
      <ChipRow>
        {options.map((o) => <Chip key={o.value} label={o.label} selected={o.value === value} onPress={() => onChange(o.value)} />)}
      </ChipRow>
    </View>
  );
}

export function Row({ children, style }: { children: React.ReactNode; style?: ViewStyle }) {
  return <View style={[{ flexDirection: 'row', alignItems: 'center', gap: space.sm }, style]}>{children}</View>;
}

export function Loading() {
  const c = usePalette();
  return <View style={{ padding: space.xl, alignItems: 'center' }}><ActivityIndicator color={c.brand} /></View>;
}

export function Empty({ title, body }: { title: string; body?: string }) {
  return (
    <Card style={{ alignItems: 'center', paddingVertical: space.xl }}>
      <P style={{ fontWeight: '600' }}>{title}</P>
      {body ? <P muted small style={{ textAlign: 'center' }}>{body}</P> : null}
    </Card>
  );
}

export function ErrorBox({ error, onRetry }: { error: unknown; onRetry?: () => void }) {
  const c = usePalette();
  const msg = error instanceof Error ? error.message : 'Something went wrong';
  return (
    <View style={{ backgroundColor: c.badBg, borderRadius: radius.md, padding: space.md, gap: space.sm }}>
      <P style={{ color: c.bad }}>{msg}</P>
      {onRetry ? <Button small kind="secondary" title="Try again" onPress={onRetry} /> : null}
    </View>
  );
}

export function Notice({ tone = 'info', children }: { tone?: 'info' | 'warn' | 'ok'; children: React.ReactNode }) {
  const c = usePalette();
  const bg = { info: c.infoBg, warn: c.warnBg, ok: c.okBg }[tone];
  const fg = { info: c.info, warn: c.warn, ok: c.ok }[tone];
  return <View style={{ backgroundColor: bg, borderRadius: radius.md, padding: space.md }}><Text style={{ color: fg, fontSize: font.small, lineHeight: 18 }}>{children}</Text></View>;
}

export function Stat({ label, value, tone }: { label: string; value: string | number; tone?: keyof Palette }) {
  const c = usePalette();
  return (
    <Card style={{ flex: 1, minWidth: 96 }}>
      <Text style={{ fontSize: font.big, fontWeight: '700', color: tone ? (c[tone] as string) : c.text }}>{value}</Text>
      <P muted small>{label}</P>
    </Card>
  );
}

export const styles = StyleSheet.create({ grow: { flex: 1 } });
