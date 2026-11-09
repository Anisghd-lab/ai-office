package com.ghdinteractivestudio.aioffice.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable

private val GlassDarkColorScheme = darkColorScheme(
    primary = NeonCyan,
    onPrimary = DeepBlackBg,
    secondary = NeonEmerald,
    onSecondary = DeepBlackBg,
    tertiary = NeonAmber,
    background = DeepBlackBg,
    onBackground = TextPrimary,
    surface = GraphiteSurface,
    onSurface = TextPrimary,
    error = NeonRose,
    onError = DeepBlackBg
)

@Composable
fun AIOfficeTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = GlassDarkColorScheme,
        content = content
    )
}
