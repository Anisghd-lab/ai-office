package com.ghdinteractivestudio.aioffice.data

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.flowOn
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import java.io.BufferedReader
import java.io.InputStreamReader
import java.util.concurrent.TimeUnit

data class SseMessage(
    val event: String,
    val data: String
)

class SseClient(
    private val sseUrl: String = "http://127.0.0.1:8000/api/v1/events/stream"
) {
    private val client = OkHttpClient.Builder()
        .readTimeout(0, TimeUnit.MILLISECONDS) // Indefinite read timeout for SSE stream
        .build()

    fun observeEvents(): Flow<SseMessage> = flow {
        var backoffMs = 1000L

        while (true) {
            try {
                val req = Request.Builder()
                    .url(sseUrl)
                    .addHeader("Accept", "text/event-stream")
                    .build()

                client.newCall(req).execute().use { response ->
                    if (response.isSuccessful) {
                        backoffMs = 1000L // Reset backoff on successful connect
                        val source = response.body?.byteStream()
                        if (source != null) {
                            val reader = BufferedReader(InputStreamReader(source))
                            var currentEvent = "message"
                            var line: String? = reader.readLine()

                            while (line != null) {
                                if (line.startsWith("event:")) {
                                    currentEvent = line.substring(6).trim()
                                } else if (line.startsWith("data:")) {
                                    val data = line.substring(5).trim()
                                    emit(SseMessage(event = currentEvent, data = data))
                                    currentEvent = "message"
                                }
                                line = reader.readLine()
                            }
                        }
                    }
                }
            } catch (e: Exception) {
                // Network disconnect or server down: emit status event and wait backoff
                emit(SseMessage(event = "disconnected", data = e.message ?: "Connection error"))
            }

            delay(backoffMs)
            backoffMs = (backoffMs * 2).coerceAtMost(10000L)
        }
    }.flowOn(Dispatchers.IO)
}
