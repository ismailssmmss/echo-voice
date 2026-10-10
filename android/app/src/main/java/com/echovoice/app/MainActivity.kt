package com.echovoice.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccountCircle
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import com.echovoice.app.ui.theme.EchoAccent
import com.echovoice.app.ui.theme.EchoCard
import com.echovoice.app.ui.theme.EchoDark
import com.echovoice.app.ui.theme.EchoMuted
import com.echovoice.app.ui.theme.EchoSurface
import com.echovoice.app.ui.theme.EchoText
import com.echovoice.app.ui.theme.EchoVoiceTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { EchoVoiceTheme { EchoVoiceApp() } }
    }
}

private enum class MainTab { HOME, MODELS, PROJECTS, PROFILE }

@Composable
fun EchoVoiceApp() {
    var selectedTab by remember { mutableStateOf(MainTab.HOME) }
    Scaffold(
        containerColor = EchoDark,
        bottomBar = {
            NavigationBar(containerColor = EchoSurface, contentColor = EchoText) {
                listOf(
                    MainTab.HOME to "Home",
                    MainTab.MODELS to "Models",
                    MainTab.PROJECTS to "Projects",
                    MainTab.PROFILE to "Profile",
                ).forEach { (tab, label) ->
                    NavigationBarItem(
                        selected = selectedTab == tab,
                        onClick = { selectedTab = tab },
                        icon = {
                            val icon = when (tab) {
                                MainTab.HOME -> Icons.Default.Home
                                MainTab.MODELS -> Icons.Default.Mic
                                MainTab.PROJECTS -> Icons.Default.PlayArrow
                                MainTab.PROFILE -> Icons.Default.AccountCircle
                            }
                            Icon(icon, contentDescription = label)
                        },
                        label = { Text(label) },
                    )
                }
            }
        },
    ) { padding ->
        Surface(
            modifier = Modifier.fillMaxSize().padding(padding),
            color = EchoDark,
        ) {
            when (selectedTab) {
                MainTab.HOME -> HomeScreen(onCreateProject = { selectedTab = MainTab.PROJECTS })
                MainTab.MODELS -> VoiceModelsScreen()
                MainTab.PROJECTS -> ProjectsScreen()
                MainTab.PROFILE -> ProfileScreen()
            }
        }
    }
}

@Composable
private fun PageColumn(content: @Composable androidx.compose.foundation.layout.ColumnScope.() -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize().background(EchoDark).padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
        content = content,
    )
}

@Composable
fun HomeScreen(onCreateProject: () -> Unit = {}) {
    PageColumn {
        Text("Echo Voice", style = MaterialTheme.typography.headlineLarge, color = EchoText)
        Text("Create voiceovers using voices you own or have permission to use.", color = EchoMuted)

        Card(
            colors = CardDefaults.cardColors(containerColor = EchoCard),
            shape = RoundedCornerShape(20.dp),
            modifier = Modifier.fillMaxWidth(),
        ) {
            Column(Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text("Create a voice project", color = EchoText, style = MaterialTheme.typography.titleLarge)
                Text(
                    "Prepare a recording, check consent, and submit a job when the service is configured.",
                    color = EchoMuted,
                )
                Button(
                    onClick = onCreateProject,
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(containerColor = EchoAccent),
                ) { Text("View projects") }
            }
        }

        Text("Service status", color = EchoText, style = MaterialTheme.typography.titleLarge)
        StatusCard("Voice generation", "Not connected to inference yet")
        StatusCard("Cloud library", "Authentication and storage setup required")
        StatusCard("Billing", "Not configured")
    }
}

@Composable
private fun StatusCard(title: String, detail: String) {
    Card(
        colors = CardDefaults.cardColors(containerColor = EchoCard),
        shape = RoundedCornerShape(16.dp),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(title, color = EchoText, style = MaterialTheme.typography.titleMedium)
            Text(detail, color = EchoMuted)
        }
    }
}

@Composable
fun VoiceModelsScreen() {
    val candidates = listOf(
        "OpenVoice V2" to "Candidate — license and quality evaluation required",
        "XTTS-v2" to "Candidate — review current checkpoint terms and language benchmarks",
        "F5-TTS" to "Research candidate — verify commercial-use license",
    )
    PageColumn {
        Text("Voice models", color = EchoText, style = MaterialTheme.typography.headlineMedium)
        Text(
            "These are evaluation candidates, not claims of currently enabled or tested models.",
            color = EchoMuted,
        )
        candidates.forEach { (name, desc) ->
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = EchoCard),
                shape = RoundedCornerShape(18.dp),
            ) {
                Column(Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier.width(10.dp).height(10.dp)
                                .clip(RoundedCornerShape(50)).background(Color(0xFF9296A3)),
                        )
                        Spacer(Modifier.width(10.dp))
                        Text(name, color = EchoText, style = MaterialTheme.typography.titleLarge)
                    }
                    Text(desc, color = EchoMuted)
                }
            }
        }
    }
}

@Composable
fun ProjectsScreen() {
    PageColumn {
        Text("Projects", color = EchoText, style = MaterialTheme.typography.headlineMedium)
        StatusCard("No cloud projects loaded", "Sign-in and project API integration are not complete.")
        StatusCard("Voice jobs", "Background processing and persistent job status are not connected.")
    }
}

@Composable
fun ProfileScreen() {
    var email by remember { mutableStateOf("") }
    PageColumn {
        Text("Profile", color = EchoText, style = MaterialTheme.typography.headlineMedium)
        OutlinedTextField(
            value = email,
            onValueChange = { email = it },
            label = { Text("Email (UI only; login is not connected)") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth(),
        )
        Text(
            "Authentication, account sync, subscriptions, and profile saving are not implemented in this screen yet.",
            color = EchoMuted,
        )
    }
}
