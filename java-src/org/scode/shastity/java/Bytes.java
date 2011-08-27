package org.scode.shastity.java;

import java.io.UnsupportedEncodingException;
import java.util.Arrays;

/**
 * Bytes is a thin wrapper around a byte[] array which allows treating bytestrings as values, and avoids
 * accidentally leaking mutable state. The underlying byte[] is accessible by explicit request, so there is no
 * strict immutability enforced.
 */
public class Bytes {
    public static final Bytes EMPTY = new Bytes();

    private static final char[] hexAlphas = new char[]
            {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f'};

    private byte[] array;

    /**
     * Create an empty Bytes.
     */
    public Bytes() {
        this.array = new byte[0];
    }

    /**
     * Create a Bytes instance by copying the given byte[].
     *
     * @param bytes The byte[] to copy.
     */
    public Bytes(byte[] bytes) {
        this(bytes, true);
    }

    /**
     * Private constructor allowing copying or not. Not exposed because non-copying
     * construction should be terribly obivous in calling code.
     */
    private Bytes(byte[] bytes, boolean copy) {
        if (copy) {
            this.array = new byte[bytes.length];
            System.arraycopy(bytes, 0, this.array, 0, bytes.length);
        } else {
            this.array = bytes;
        }
    }

    /**
     * Construct a Bytes wrapping the given array, not doing any copying. Bytes will assume
     * that the caller is transfering complete ownership of the byte array and that the byte
     * array will never be modified by the caller.
     *
     * @param bytes The byte[] to be wrapped.
     * @return The newly constructed Bytes.
     */
    public static Bytes wrapArray(byte[] bytes) {
        return new Bytes(bytes, false);
    }

    public byte[] getMutableByteArray() {
        return this.array;
    }

    /**
     * Equivalent of Bytes.encode(str, "UTF-8").
     *
     * @param str The string to encode
     * @return The Bytes.
     */
    public static Bytes encode(String str) {
        return Bytes.encode(str, "UTF-8");
    }

    /**
     * Construct a Bytes instance representing the given String encoded in the
     * given charset.
     *
     * @param str The string.
     * @throws RuntimeException if an UnsupportedEncodingException is thrown.
     *
     * @return The Bytes instance.
     */
    public static Bytes encode(String str, String charset) {
        // Rely on String.getBytes() returning something we own.
        try {
            return Bytes.wrapArray(str.getBytes("UTF-8"));
        } catch (UnsupportedEncodingException e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * Return a Bytes instance containing the bytes reprecented hexadecimally (lower case alphas) in the
     * given string.
     *
     * @param hex The hex string.
     *
     * @throws IllegalArgumentException if the hexadeciaml string cannot be parsed
     *
     * @return The Bytes instance.
     */
    public static Bytes fromHex(String hex) {
        if (hex.length() % 2 != 0) {
            throw new IllegalArgumentException("hexadecimal strings must be of even length");
        }

        byte[] arr = new byte[hex.length() / 2];

        for (int i = 0; i < arr.length; i++) {
            int v1 = Character.digit(hex.charAt(i * 2), 16) << 4;
            int v2 = Character.digit(hex.charAt(i * 2 + 1), 16);

            if (v1 == -1 || v2 == -1) {
                throw new IllegalArgumentException("invalid hex character encountered");
            }

            arr[i] = (byte)(v1 | v2);
        }

        return Bytes.wrapArray(arr);
    }

    /**
     * Return a hexadecimal string representing this Bytes.
     *
     * @return The hexadeciaml string.
     */
    public String toHex() {
        StringBuffer sb = new StringBuffer();

        for (int b : this.array) {
            sb.append(hexAlphas[b >> 4]);
            sb.append(hexAlphas[b & 0x0F]);
        }
        return sb.toString();
    }

    /**
     * Equivalent of decode("UTF-8").
     * 
     * @return The decoded string.
     */
    public String decode() {
        return this.decode("UTF-8");
    }

    /**
     * @throws RuntimeException if an UnsupportedEncodingException is thrown
     *
     * @param charset The
     *
     * @return The string.
     */
    public String decode(String charset) {
        try {
            return new String(this.array, "UTF-8");
        } catch (UnsupportedEncodingException e) {
            throw new RuntimeException(e);
        }
    }

    public String toString() {
        return "<" + this.toHex() + ">";
    }

    public int length() {
        return this.array.length;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;

        Bytes bytes = (Bytes) o;

        if (!Arrays.equals(array, bytes.array)) return false;

        return true;
    }

    @Override
    public int hashCode() {
        return array != null ? Arrays.hashCode(array) : 0;
    }
}
