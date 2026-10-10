package com.echovoice.app

import android.content.Context
import android.net.Uri
import android.provider.OpenableColumns
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.File
import java.io.IOException
import java.net.URI
import java.util.concurrent.TimeUnit

data class AuthSession(val accessToken: String, val email: String)

object EchoVoiceApi {
    private const val PREFS_NAME = "echo_voice_settings"
    private const val API_URL_KEY = "api_base_url"
    private const val MAX_REFERENCE_BYTES = 25 * 1024 * 1024

    fun getApiBaseUrl(context: Context): String =
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            .getString(API_URL_KEY, BuildConfig.API_BASE_URL)
            .orEmpty()
            .trim()
            .trimEnd('/')

    /**
     * Save a user-configurable backend URL so a physical Android device can
     * connect to a server on the same Wi-Fi or to a deployed HTTPS service.
     * HTTP is allowed only for loopback/emulator and private/local network hosts.
     */
    fun saveApiBaseUrl(context: Context, candidate: String): String? {
        val normalized = candidate.trim().trimEnd('/')
        val uri = try {
            URI(normalized)
        } catch (_: Exception) {
            return "عنوان الخادم غير صالح."
        }
        val scheme = uri.scheme?.lowercase()
        val host = uri.host?.lowercase()
        val path = uri.path?.trimEnd('/').orEmpty()
        if (scheme !in setOf("http", "https") || host.isNullOrBlank()) {
            return "اكتب عنواناً يبدأ بـ http:// أو https://."
        }
        if (uri.userInfo != null || uri.query != null || uri.fragment != null) {
            return "عنوان الخادم لا يجب أن يحتوي على بيانات دخول أو معاملات."
        }
        if (!path.endsWith("/api/v1")) {
            return "يجب أن ينتهي العنوان بـ /api/v1."
        }
        val localHost = host == "localhost" || host == "127.0.0.1" ||
            host == "::1" || host == "10.0.2.2" || host.endsWith(".local") ||
            host.startsWith("10.") || host.startsWith("192.168.") ||
            Regex("^172\\.(1[6-9]|2[0-9]|3[01])\\..+").matches(host)
        if (scheme == "http" && !localHost) {
            return "استخدم HTTPS للخوادم العامة. HTTP مسموح فقط للمحاكي أو الشبكة المحلية."
        }
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            .edit()
            .putString(API_URL_KEY, normalized)
            .apply()
        return null
    }

    private fun client(): OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(120, TimeUnit.SECONDS)
        .readTimeout(32, TimeUnit.MINUTES)
        .callTimeout(34, TimeUnit.MINUTES)
        .retryOnConnectionFailure(true)
        .build()

    suspend fun checkBackend(context: Context) = withContext(Dispatchers.IO) {
        val healthClient = client().newBuilder()
            .connectTimeout(5, TimeUnit.SECONDS)
            .readTimeout(10, TimeUnit.SECONDS)
            .callTimeout(15, TimeUnit.SECONDS)
            .build()
        val request = Request.Builder()
            .url("${getApiBaseUrl(context)}/health")
            .get()
            .build()
        healthClient.newCall(request).execute().use { response ->
            val body = response.body?.string().orEmpty()
            if (!response.isSuccessful) {
                throw IOException(readDetail(body, "تعذر الاتصال بخادم Echo Voice."))
            }
            val status = try {
                JSONObject(body).optString("status")
            } catch (_: Exception) {
                ""
            }
            if (status != "ok") {
                throw IOException("وصل التطبيق إلى عنوان لا يبدو أنه خادم Echo Voice API.")
            }
        }
    }

    suspend fun authenticate(
        context: Context,
        email: String,
        password: String,
        register: Boolean,
    ): AuthSession = withContext(Dispatchers.IO) {
        val payload = JSONObject()
            .put("email", email.trim())
            .put("password", password)
            .toString()
            .toRequestBody("application/json; charset=utf-8".toMediaType())
        val path = if (register) "auth/register" else "auth/login"
        val request = Request.Builder()
            .url("${getApiBaseUrl(context)}/$path")
            .post(payload)
            .build()

        client().newCall(request).execute().use { response ->
            val body = response.body?.string().orEmpty()
            if (!response.isSuccessful) {
                throw IOException(readDetail(body, "تعذر تسجيل الدخول. تحقق من البريد وكلمة المرور واتصال الخادم."))
            }
            val json = JSONObject(body)
            AuthSession(
                accessToken = json.getString("access_token"),
                email = json.optString("email", email.trim()),
            )
        }
    }

    suspend fun synthesize(
        context: Context,
        token: String,
        referenceUri: Uri,
        referenceText: String,
        text: String,
        language: String,
        consentConfirmed: Boolean,
        speed: Float,
    ): File = withContext(Dispatchers.IO) {
        val resolver = context.contentResolver
        val content = resolver.openInputStream(referenceUri)?.use { input ->
            val output = java.io.ByteArrayOutputStream()
            val buffer = ByteArray(64 * 1024)
            var total = 0
            while (true) {
                val count = input.read(buffer)
                if (count < 0) break
                total += count
                if (total > MAX_REFERENCE_BYTES) {
                    throw IOException("حجم الملف أكبر من 25 ميغابايت.")
                }
                output.write(buffer, 0, count)
            }
            output.toByteArray()
        } ?: throw IOException("لم أتمكن من قراءة الملف الصوتي المحدد.")

        if (content.isEmpty()) throw IOException("الملف الصوتي فارغ.")
        val displayName = getDisplayName(context, referenceUri)
            .replace("\"", "")
            .replace("\r", "")
            .replace("\n", "")
        val mime = (resolver.getType(referenceUri) ?: "audio/wav").toMediaType()
        val multipart = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart(
                "reference_audio",
                displayName.ifBlank { "reference.wav" },
                content.toRequestBody(mime),
            )
            .addFormDataPart("reference_text", referenceText.trim())
            .addFormDataPart("text", text.trim())
            .addFormDataPart("language", language)
            .addFormDataPart("consent_confirmed", consentConfirmed.toString())
            .addFormDataPart("speed", speed.toString())
            .build()

        val request = Request.Builder()
            .url("${getApiBaseUrl(context)}/voice-jobs/clone")
            .header("Authorization", "Bearer $token")
            .post(multipart)
            .build()

        client().newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                val detail = readDetail(response.body?.string().orEmpty(), "فشل توليد الصوت. تحقق من اتصال المحرك.")
                throw IOException(detail)
            }
            val responseType = response.header("Content-Type").orEmpty()
            if (!responseType.startsWith("audio/wav", ignoreCase = true)) {
                throw IOException("أعاد الخادم نوع ملف غير متوقع.")
            }
            val bytes = response.body?.bytes() ?: throw IOException("لم يُرجع الخادم ملفاً صوتياً.")
            if (bytes.size < 1024) throw IOException("الملف الناتج غير صالح.")

            val outputDir = File(context.filesDir, "generated-audio")
            if (!outputDir.exists() && !outputDir.mkdirs()) {
                throw IOException("تعذر إنشاء مجلد الملفات الصوتية.")
            }
            val outputFile = File(outputDir, "echovoice-${System.currentTimeMillis()}.wav")
            outputFile.writeBytes(bytes)
            outputFile
        }
    }

    fun getDisplayName(context: Context, uri: Uri): String {
        context.contentResolver.query(uri, arrayOf(OpenableColumns.DISPLAY_NAME), null, null, null)?.use { cursor ->
            val column = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
            if (column >= 0 && cursor.moveToFirst()) {
                return cursor.getString(column) ?: "reference.wav"
            }
        }
        return uri.lastPathSegment?.substringAfterLast('/') ?: "reference.wav"
    }

    private fun readDetail(body: String, fallback: String): String {
        return try {
            val json = JSONObject(body)
            json.optString("detail").takeIf { it.isNotBlank() } ?: fallback
        } catch (_: Exception) {
            fallback
        }
    }
}
