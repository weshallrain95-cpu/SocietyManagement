// Pick photos/videos from the phone's gallery (or the computer's files on the web), or take a photo.
import * as ImagePicker from 'expo-image-picker';
import { Platform } from 'react-native';

import type { UploadFile } from '@/api';

type Kind = 'photo' | 'video';

function toUpload(a: ImagePicker.ImagePickerAsset, kind: Kind): UploadFile {
  const fallback = kind === 'video' ? { name: 'walkthrough.mp4', type: 'video/mp4' } : { name: 'photo.jpg', type: 'image/jpeg' };
  return { uri: a.uri, name: a.fileName ?? fallback.name, type: a.mimeType ?? fallback.type, file: (a as { file?: File }).file };
}

export async function pickFromGallery(kind: Kind, multiple = false): Promise<UploadFile[]> {
  const r = await ImagePicker.launchImageLibraryAsync({
    mediaTypes: kind === 'video' ? ['videos'] : ['images'],
    allowsMultipleSelection: multiple,
    selectionLimit: multiple ? 10 : 1,
    quality: 0.9,
    videoMaxDuration: 180,
  });
  return r.canceled ? [] : r.assets.map((a) => toUpload(a, kind));
}

/** Phones only: the web has no camera access inside the preview. */
export const canUseCamera = Platform.OS !== 'web';

export async function takePhoto(): Promise<UploadFile[]> {
  const perm = await ImagePicker.requestCameraPermissionsAsync();
  if (!perm.granted) throw new Error('Allow camera access in your phone settings to take photos.');
  const r = await ImagePicker.launchCameraAsync({ mediaTypes: ['images'], quality: 0.9 });
  return r.canceled ? [] : r.assets.map((a) => toUpload(a, 'photo'));
}
