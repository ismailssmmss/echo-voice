package com.echovoice.app

import android.media.MediaPlayer
import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccountCircle
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Checkbox
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Slider
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import com.echovoice.app.ui.theme.EchoAccent
import com.echovoice.app.ui.theme.EchoCard
import com.echovoice.app.ui.theme.EchoDark
import com.echovoice.app.ui.theme.EchoMuted
import com.echovoice.app.ui.theme.EchoSurface
import com.echovoice.app.ui.theme.EchoText
import com.echovoice.app.ui.theme.EchoVoiceTheme
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { EchoVoiceTheme { EchoVoiceApp() } }
    }
}

private enum class MainTab { HOME, MODELS, PROJECTS, PROFILE }

@Composable
fun EchoVoiceApp() {
    var session by remember { mutableStateOf<AuthSession?>(null) }
    var selectedTab by remember { mutableStateOf(MainTab.HOME) }
    var latestOutputPath by remember { mutableStateOf<String?>(null) }

    if (session == null) {
        AuthenticationScreen(onAuthenticated = { session = it })
        return
    }

    val activeSession = session ?: return
    Scaffold(
        containerColor = EchoDark,
        bottomBar = {
            NavigationBar(containerColor = EchoSurface, contentColor = EchoText) {
                listOf(
                    MainTab.HOME to "Studio",
                    MainTab.MODELS to "Model",
                    MainTab.PROJECTS to "Audio",
                    MainTab.PROFILE to "Account",
                ).forEach { (tab, label) ->
                    NavigationBarItem(
                        selected = selectedTab == tab,
                        onClick = { selectedTab = tab },
                        icon = {
                            val icon = when (tab) {
                                MainTab.HOME -> Icons.Default.Home
                                MainTab.MODELS -> Icons.Default.PlayArrow
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
                MainTab.HOME -> VoiceStudioScreen(
                    token = activeSession.accessToken,
                    latestOutputPath = latestOutputPath,
                    onOutputReady = { latestOutputPath = it },
                )
                MainTab.MODELS -> VoiceModelsScreen()
                MainTab.PROJECTS -> AudioLibraryScreen(latestOutputPath)
                MainTab.PROFILE -> ProfileScreen(activeSession.email) {
                    session = null
                    selectedTab = MainTab.HOME
                }
            }
        }
    }
}

@Composable
private fun PageColumn(content: @Composable androidx.compose.foundation.layout.ColumnScope.() -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize()
            .background(EchoDark)
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
        content = content,
    )
}

@Composable
private fun AuthenticationScreen(onAuthenticated: (AuthSession) -> Unit) {
    val context = LocalContext.current
    var apiBaseUrl by remember { mutableStateOf(EchoVoiceApi.getApiBaseUrl(context)) }
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var createAccount by remember { mutableStateOf(false) }
    var busy by remember { mutableStateOf(false) }
    var checkingBackend by remember { mutableStateOf(false) }
    var message by remember { mutableStateOf("") }
    val scope = rememberCoroutineScope()

    Surface(modifier = Modifier.fillMaxSize(), color = EchoDark) {
        Column(
            modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(24.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text("Echo Voice", style = MaterialTheme.typography.headlineLarge, color = EchoText)
            Spacer(Modifier.height(8.dp))
            Text("استنساخ الصوت وتوليد الكلام", color = EchoMuted)
            Spacer(Modifier.height(16.dp))
            OutlinedTextField(
                value = apiBaseUrl,
                onValueChange = { apiBaseUrl = it.take(512) },
                label = { Text("عنوان خادم API") },
                placeholder = { Text("https://your-server.example/api/v1") },
                supportingText = {
                    Text(
                        "المحاكي: http://10.0.2.2:8000/api/v1. للهاتف الحقيقي استخدم IP الخادم على شبكة Wi-Fi أو عنوان HTTPS.",
                        color = EchoMuted,
                    )
                },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
            OutlinedButton(
                enabled = !busy && !checkingBackend,
                onClick = {
                    val error = EchoVoiceApi.saveApiBaseUrl(context, apiBaseUrl)
                    if (error != null) {
                        message = error
                    } else {
                        scope.launch {
                            checkingBackend = true
                            message = "جارٍ فحص اتصال الخادم..."
                            try {
                                EchoVoiceApi.checkBackend(context)
                                message = "نجح الاتصال بواجهة Echo Voice API. أصبح بإمكانك تسجيل الدخول."
                            } catch (failure: Exception) {
                                message = failure.message ?: "تعذر الوصول إلى الخادم. تأكد أنه يعمل وأن الهاتف يستطيع الوصول إليه."
                            } finally {
                                checkingBackend = false
                            }
                        }
                    }
                },
                modifier = Modifier.fillMaxWidth(),
            ) { Text(if (checkingBackend) "جارٍ الفحص..." else "حفظ العنوان وفحص الاتصال") }
            Spacer(Modifier.height(12.dp))
            OutlinedTextField(
                value = email,
                onValueChange = { email = it },
                label = { Text("البريد الإلكتروني") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
            OutlinedTextField(
                value = password,
                onValueChange = { password = it },
                label = { Text("كلمة المرور (8 أحرف على الأقل)") },
                visualTransformation = PasswordVisualTransformation(),
                singleLine = true,
                modifier = Modifier.fillMaxWidth().padding(top = 10.dp),
            )
            Button(
                enabled = !busy && !checkingBackend && email.contains("@") && password.length >= 8,
                onClick = {
                    scope.launch {
                        busy = true
                        message = if (createAccount) "جارٍ إنشاء الحساب..." else "جارٍ تسجيل الدخول..."
                        try {
                            val configError = EchoVoiceApi.saveApiBaseUrl(context, apiBaseUrl)
                            if (configError != null) throw IllegalArgumentException(configError)
                            val result = EchoVoiceApi.authenticate(context, email, password, createAccount)
                            onAuthenticated(result)
                        } catch (error: Exception) {
                            message = error.message ?: "تعذر الاتصال بالخادم."
                        } finally {
                            busy = false
                        }
                    }
                },
                modifier = Modifier.fillMaxWidth().padding(top = 18.dp),
                colors = ButtonDefaults.buttonColors(containerColor = EchoAccent),
            ) {
                Text(if (busy) "يرجى الانتظار..." else if (createAccount) "إنشاء حساب" else "تسجيل الدخول")
            }
            OutlinedButton(
                onClick = {
                    createAccount = !createAccount
                    message = ""
                },
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(if (createAccount) "لديك حساب؟ تسجيل الدخول" else "إنشاء حساب جديد")
            }
            if (message.isNotBlank()) {
                Text(message, color = EchoMuted, modifier = Modifier.padding(top = 8.dp))
            }
            Text(
                "يتطلب الاتصال بخادم Echo Voice مضبوط ومتاح. في المحاكي يستخدم التطبيق العنوان المحلي الافتراضي.",
                color = EchoMuted,
                style = MaterialTheme.typography.bodySmall,
                modifier = Modifier.padding(top = 18.dp),
            )
        }
    }
}

@Composable
private fun VoiceStudioScreen(
    token: String,
    latestOutputPath: String?,
    onOutputReady: (String) -> Unit,
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    var referenceUri by remember { mutableStateOf<Uri?>(null) }
    var referenceName by remember { mutableStateOf("") }
    var referenceText by remember { mutableStateOf("") }
    var speechText by remember {
        mutableStateOf("أهلاً بك في Echo Voice. هذا مثال على توليد الكلام باستخدام الذكاء الاصطناعي.")
    }
    var language by remember { mutableStateOf("ar") }
    var languageMenuExpanded by remember { mutableStateOf(false) }
    var consent by remember { mutableStateOf(false) }
    var speed by remember { mutableStateOf(1.0f) }
    var busy by remember { mutableStateOf(false) }
    var message by remember { mutableStateOf("") }
    var player by remember { mutableStateOf<MediaPlayer?>(null) }

    DisposableEffect(Unit) {
        onDispose { player?.release() }
    }

    val audioPicker = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.OpenDocument(),
    ) { uri ->
        if (uri != null) {
            referenceUri = uri
            referenceName = EchoVoiceApi.getDisplayName(context, uri)
            message = "تم تحديد التسجيل. تأكد أن النص المرجعي يطابق أول 8 ثوانٍ منه."
        }
    }
    val outputFile = latestOutputPath?.let(::File)?.takeIf { it.isFile }
    val exportLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.CreateDocument("audio/wav"),
    ) { destination ->
        val file = outputFile
        if (destination != null && file != null) {
            scope.launch {
                try {
                    withContext(Dispatchers.IO) {
                        context.contentResolver.openOutputStream(destination)?.use { target ->
                            file.inputStream().use { source -> source.copyTo(target) }
                        } ?: throw IllegalStateException("تعذر إنشاء ملف التصدير.")
                    }
                    message = "تم حفظ الملف في الموقع المحدد."
                } catch (error: Exception) {
                    message = error.message ?: "تعذر تصدير الملف."
                }
            }
        }
    }

    fun playOutput(file: File) {
        try {
            player?.release()
            player = MediaPlayer().apply {
                setDataSource(file.absolutePath)
                setOnPreparedListener { it.start() }
                setOnCompletionListener {
                    it.release()
                    if (player === it) player = null
                }
                setOnErrorListener { mediaPlayer, _, _ ->
                    mediaPlayer.release()
                    if (player === mediaPlayer) player = null
                    message = "تعذر تشغيل الصوت الناتج."
                    true
                }
                prepareAsync()
            }
            message = "جارٍ تشغيل الصوت الناتج..."
        } catch (error: Exception) {
            message = error.message ?: "تعذر تشغيل الصوت الناتج."
        }
    }

    PageColumn {
        Text("Echo Voice Studio", style = MaterialTheme.typography.headlineLarge, color = EchoText)
        Text(
            "استنسخ صوتاً تملك حق استخدامه ثم أنشئ كلاماً عربياً أو إنجليزياً.",
            color = EchoMuted,
        )

        Card(
            colors = CardDefaults.cardColors(containerColor = EchoCard),
            shape = RoundedCornerShape(20.dp),
            modifier = Modifier.fillMaxWidth(),
        ) {
            Column(Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text("1. التسجيل المرجعي", color = EchoText, style = MaterialTheme.typography.titleLarge)
                Text(
                    "اختر تسجيلاً واضحاً مدته 3–120 ثانية. سيستخدم المحرك أول 8 ثوانٍ فقط؛ أدخل التفريغ النصي المطابق لهذه المدة.",
                    color = EchoMuted,
                )
                OutlinedButton(
                    onClick = { audioPicker.launch(arrayOf("audio/*")) },
                    modifier = Modifier.fillMaxWidth(),
                ) { Text(if (referenceName.isBlank()) "اختيار ملف صوتي" else "الملف: $referenceName") }
                OutlinedTextField(
                    value = referenceText,
                    onValueChange = { referenceText = it.take(2000) },
                    label = { Text("النص المنطوق في أول 8 ثوانٍ") },
                    modifier = Modifier.fillMaxWidth(),
                    minLines = 2,
                )

                Text("2. النص المطلوب توليده", color = EchoText, style = MaterialTheme.typography.titleLarge)
                OutlinedTextField(
                    value = speechText,
                    onValueChange = { speechText = it.take(5000) },
                    label = { Text("النص العربي أو الإنجليزي") },
                    modifier = Modifier.fillMaxWidth(),
                    minLines = 4,
                )

                Text("لغة الناتج", color = EchoText)
                Box {
                    OutlinedButton(onClick = { languageMenuExpanded = true }) {
                        Text(
                            when (language) {
                                "en" -> "English"
                                "ar-en" -> "عربي + English"
                                else -> "العربية"
                            }
                        )
                    }
                    DropdownMenu(
                        expanded = languageMenuExpanded,
                        onDismissRequest = { languageMenuExpanded = false },
                    ) {
                        listOf("ar" to "العربية", "en" to "English", "ar-en" to "عربي + English").forEach { (value, label) ->
                            DropdownMenuItem(
                                text = { Text(label) },
                                onClick = {
                                    language = value
                                    languageMenuExpanded = false
                                },
                            )
                        }
                    }
                }

                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("سرعة الكلام: ${String.format("%.2f", speed)}×", color = EchoText)
                    Spacer(Modifier.width(12.dp))
                }
                Slider(
                    value = speed,
                    onValueChange = { speed = it },
                    valueRange = 0.75f..1.25f,
                )

                Row(verticalAlignment = Alignment.Top) {
                    Checkbox(checked = consent, onCheckedChange = { consent = it })
                    Text(
                        "أؤكد أن الصوت صوتي أو لدي إذن صريح من صاحبه. أوافق على تسجيل الموافقة، وأتعهد بالإفصاح أن الناتج مولّد بالذكاء الاصطناعي.",
                        color = EchoMuted,
                        modifier = Modifier.padding(top = 10.dp),
                    )
                }

                Button(
                    enabled = !busy && referenceUri != null && referenceText.trim().length >= 2 &&
                        speechText.trim().isNotEmpty() && consent,
                    onClick = {
                        val uri = referenceUri ?: return@Button
                        scope.launch {
                            busy = true
                            message = "جارٍ تجهيز التسجيل وتشغيل المحرك. قد يستغرق التحميل الأول للنموذج عدة دقائق."
                            try {
                                val file = EchoVoiceApi.synthesize(
                                    context = context,
                                    token = token,
                                    referenceUri = uri,
                                    referenceText = referenceText,
                                    text = speechText,
                                    language = language,
                                    consentConfirmed = consent,
                                    speed = speed,
                                )
                                onOutputReady(file.absolutePath)
                                message = "اكتمل التوليد. تم حفظ نسخة محلية داخل التطبيق."
                            } catch (error: Exception) {
                                message = error.message ?: "تعذر توليد الصوت. تحقق من الخادم والمحرك."
                            } finally {
                                busy = false
                            }
                        }
                    },
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(containerColor = EchoAccent),
                ) {
                    Text(if (busy) "جارٍ توليد الصوت..." else "استنساخ الصوت وتوليد WAV")
                }
            }
        }

        if (message.isNotBlank()) StatusCard("حالة العملية", message)
        if (outputFile != null) {
            Card(
                colors = CardDefaults.cardColors(containerColor = EchoCard),
                shape = RoundedCornerShape(18.dp),
                modifier = Modifier.fillMaxWidth(),
            ) {
                Column(Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text("الصوت الناتج", color = EchoText, style = MaterialTheme.typography.titleLarge)
                    Text(outputFile.name, color = EchoMuted)
                    Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                        Button(onClick = { playOutput(outputFile) }, colors = ButtonDefaults.buttonColors(containerColor = EchoAccent)) {
                            Text("تشغيل")
                        }
                        OutlinedButton(onClick = {
                            exportLauncher.launch("echovoice-ai-generated.wav")
                        }) { Text("تصدير WAV") }
                    }
                    Text("هذا الملف ناتج بالذكاء الاصطناعي. احتفظ بوضوح الإفصاح عند مشاركته.", color = EchoMuted)
                }
            }
        }
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
private fun VoiceModelsScreen() {
    PageColumn {
        Text("Voice engine", color = EchoText, style = MaterialTheme.typography.headlineMedium)
        StatusCard(
            "SILMA TTS v1",
            "محرك استنساخ صوت فعلي يدعم العربية والإنجليزية والنص المختلط. يتم تحميل الأوزان عند أول طلب وتخزينها في ذاكرة النموذج الدائمة للخادم.",
        )
        StatusCard(
            "حدود الاستخدام",
            "الإصدار الحالي لا يدعم كل اللغات. التفريغ النصي للتسجيل المرجعي مطلوب، ويجب أن يطابق أول 8 ثوانٍ من المقطع المستخدم.",
        )
        StatusCard(
            "الخصوصية",
            "يُرسل التسجيل إلى خادم المحرك لمعالجته، ثم تُحذف الملفات المؤقتة بعد الاستجابة. لا يتم رفعه إلى مكتبة سحابية في الإصدار الحالي.",
        )
    }
}

@Composable
private fun AudioLibraryScreen(latestOutputPath: String?) {
    val file = latestOutputPath?.let(::File)?.takeIf { it.isFile }
    PageColumn {
        Text("ملفات الصوت", color = EchoText, style = MaterialTheme.typography.headlineMedium)
        if (file == null) {
            StatusCard("لا توجد ملفات بعد", "أنشئ ملفاً من صفحة Studio وسيظهر آخر ملف محفوظ داخل التطبيق هنا.")
        } else {
            StatusCard("آخر ملف", "${file.name} • ${file.length() / 1024} KB")
            Text(
                "الملف محفوظ في مساحة التطبيق الخاصة. استخدم زر تصدير WAV في صفحة Studio لحفظ نسخة في مجلد تختاره.",
                color = EchoMuted,
            )
        }
    }
}

@Composable
private fun ProfileScreen(email: String, onSignOut: () -> Unit) {
    PageColumn {
        Text("الحساب", color = EchoText, style = MaterialTheme.typography.headlineMedium)
        StatusCard("تم تسجيل الدخول", email)
        StatusCard(
            "المزامنة",
            "إصدار المعاينة لا يحفظ رموز الدخول محلياً بعد إغلاق التطبيق ولا يدعم مكتبة صوت سحابية بعد.",
        )
        Button(onClick = onSignOut, modifier = Modifier.fillMaxWidth()) {
            Text("تسجيل الخروج")
        }
    }
}
