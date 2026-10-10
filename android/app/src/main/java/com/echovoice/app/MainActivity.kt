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
import androidx.compose.material3.ExperimentalMaterial3Api
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
import androidx.compose.ui.unit.sp
import com.echovoice.app.ui.theme.EchoAccent
import com.echovoice.app.ui.theme.EchoCard
import com.echovoice.app.ui.theme.EchoDark
import com.echovoice.app.ui.theme.EchoGreen
import com.echovoice.app.ui.theme.EchoMuted
import com.echovoice.app.ui.theme.EchoSurface
import com.echovoice.app.ui.theme.EchoText
import com.echovoice.app.ui.theme.EchoVoiceTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            EchoVoiceTheme {
                EchoVoiceApp()
            }
        }
    }
}

enum class MainTab {
    HOME,
    MODELS,
    PROJECTS,
    PROFILE,
}

@Composable
fun EchoVoiceApp() {
    var selectedTab by remember { mutableStateOf(MainTab.HOME) }

    Scaffold(
        containerColor = EchoDark,
        bottomBar = {
            NavigationBar(
                containerColor = EchoSurface,
                contentColor = EchoText,
            ) {
                val tabs = listOf(
                    MainTab.HOME to "Home",
                    MainTab.MODELS to "Models",
                    MainTab.PROJECTS to "Projects",
                    MainTab.PROFILE to "Profile",
                )

                tabs.forEach { (tab, label) ->
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
    ) { innerPadding ->
        Surface(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding),
            color = EchoDark,
        ) {
            when (selectedTab) {
                MainTab.HOME -> HomeScreen()
                MainTab.MODELS -> VoiceModelsScreen()
                MainTab.PROJECTS -> ProjectsScreen()
                MainTab.PROFILE -> ProfileScreen()
            }
        }
    }
}

@Composable
fun HomeScreen() {
    val stats = listOf(
        "12,430" to "voices generated",
        "184" to "jobs active",
        "96%" to "model uptime",
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(EchoDark)
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(18.dp),
    ) {
        Text(
            text = "Echo Voice",
            style = MaterialTheme.typography.headlineLarge,
            color = EchoText,
        )

        Text(
            text = "Create high-quality voiceovers in minutes.",
            style = MaterialTheme.typography.bodyLarge,
            color = EchoMuted,
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            stats.forEach { (value, label) ->
                Card(
                    modifier = Modifier.weight(1f),
                    colors = CardDefaults.cardColors(containerColor = EchoCard),
                    shape = RoundedCornerShape(18.dp),
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(6.dp),
                    ) {
                        Text(value, color = EchoText, style = MaterialTheme.typography.titleLarge)
                        Text(label, color = EchoMuted, style = MaterialTheme.typography.bodyMedium)
                    }
                }
            }
        }

        Card(
            colors = CardDefaults.cardColors(containerColor = EchoCard),
            shape = RoundedCornerShape(20.dp),
            modifier = Modifier.fillMaxWidth(),
        ) {
            Column(
                modifier = Modifier.padding(20.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                Text("Generate narration", color = EchoText, style = MaterialTheme.typography.titleLarge)
                Text(
                    "Turn scripts into voiceovers with a selected voice model and custom timing.",
                    color = EchoMuted,
                )
                Button(
                    onClick = { },
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(containerColor = EchoAccent),
                ) {
                    Text("Create new project")
                }
            }
        }

        Text("Recent activity", color = EchoText, style = MaterialTheme.typography.titleLarge)
        LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp)) {
            items(
                listOf(
                    "Voice model trained successfully",
                    "Script "Hello introduction" rendered",
                    "Subscription renewed",
                )
            ) { item ->
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(14.dp))
                        .background(EchoSurface)
                        .padding(14.dp),
                ) {
                    Text(item, color = EchoText)
                }
            }
        }
    }
}

@Composable
fun VoiceModelsScreen() {
    val models = listOf(
        "OpenVoice V2" to "Commercial quality voice clone",
        "XTTS-v2" to "Multilingual and fast generation",
        "F5-TTS" to "Research preview",
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(EchoDark)
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(18.dp),
    ) {
        Text("Voice models", color = EchoText, style = MaterialTheme.typography.headlineMedium)
        models.forEach { (name, desc) ->
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = EchoCard),
                shape = RoundedCornerShape(18.dp),
            ) {
                Column(modifier = Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier
                                .width(12.dp)
                                .height(12.dp)
                                .background(EchoGreen, shape = RoundedCornerShape(50)),
                        )
                        Spacer(modifier = Modifier.width(10.dp))
                        Text(name, color = EchoText, style = MaterialTheme.typography.titleLarge)
                    }
                    Text(desc, color = EchoMuted)
                    Button(
                        onClick = { },
                        colors = ButtonDefaults.buttonColors(containerColor = EchoAccent),
                    ) {
                        Text("Use model")
                    }
                }
            }
        }
    }
}

@Composable
fun ProjectsScreen() {
    val projects = listOf(
        "Brand intro" to "In progress",
        "Tutorial narration" to "Queued",
        "Podcast episode" to "Completed",
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(EchoDark)
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Text("Projects", color = EchoText, style = MaterialTheme.typography.headlineMedium)

        projects.forEach { (title, status) ->
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = EchoCard),
                shape = RoundedCornerShape(18.dp),
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(18.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Column {
                        Text(title, color = EchoText, style = MaterialTheme.typography.titleLarge)
                        Text(status, color = EchoMuted)
                    }
                    Button(
                        onClick = { },
                        colors = ButtonDefaults.buttonColors(containerColor = EchoAccent),
                    ) {
                        Text("Open")
                    }
                }
            }
        }
    }
}

@Composable
fun ProfileScreen() {
    var email by remember { mutableStateOf("user@echovoice.app") }
    var password by remember { mutableStateOf("********") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(EchoDark)
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(18.dp),
    ) {
        Text("Profile", color = EchoText, style = MaterialTheme.typography.headlineMedium)

        OutlinedTextField(
            value = email,
            onValueChange = { email = it },
            label = { Text("Email") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth(),
        )

        OutlinedTextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Password") },
            singleLine = true,
            visualTransformation = PasswordVisualTransformation(),
            modifier = Modifier.fillMaxWidth(),
        )

        Button(
            onClick = { },
            modifier = Modifier.fillMaxWidth(),
            colors = ButtonDefaults.buttonColors(containerColor = EchoAccent),
        ) {
            Text("Save profile")
        }
    }
}
