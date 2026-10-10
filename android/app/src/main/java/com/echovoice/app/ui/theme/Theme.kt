package com.echovoice.app.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

private val DarkColorScheme = darkColorScheme(
    primary = EchoAccent,
    secondary = EchoAccentSoft,
    tertiary = EchoGreen,
    background = EchoDark,
    surface = EchoSurface,
    onPrimary = EchoText,
    onSecondary = EchoText,
    onBackground = EchoText,
    onSurface = EchoText,
)

private val LightColorScheme = lightColorScheme(
    primary = EchoAccent,
    secondary = EchoAccentSoft,
    tertiary = EchoGreen,
    background = androidx.compose.ui.graphics.Color.White,
    surface = androidx.compose.ui.graphics.Color.White,
    onPrimary = androidx.compose.ui.graphics.Color.Black,
    onSecondary = androidx.compose.ui.graphics.Color.Black,
    onBackground = androidx.compose.ui.graphics.Color.Black,
    onSurface = androidx.compose.ui.graphics.Color.Black,
)

@Composable
fun EchoVoiceTheme(
    darkTheme: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme
    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content,
    )
}
