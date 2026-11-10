package com.ghdinteractivestudio.aioffice.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.ghdinteractivestudio.aioffice.data.TermuxBridge
import com.ghdinteractivestudio.aioffice.ui.components.GlassCard
import com.ghdinteractivestudio.aioffice.ui.theme.*
import com.ghdinteractivestudio.aioffice.viewmodel.OfficeViewModel

@Composable
fun VideoEngineControlScreen(viewModel: OfficeViewModel) {
    val context = LocalContext.current
    val flowkitStatus by viewModel.flowkitStatus.collectAsState()
    val logs by viewModel.flowkitLogs.collectAsState()

    val stateColor = when (flowkitStatus.state) {
        "RUNNING" -> NeonEmerald
        "WAITING_FOR_BROWSER" -> NeonAmber
        "DEGRADED" -> NeonAmber
        "STOPPED" -> NeonRose
        else -> TextSecondary
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Title
        Text(
            text = "FLOWKIT VIDEO ENGINE",
            color = NeonCyan,
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold
        )

        // Engine Status Banner
        GlassCard(
            modifier = Modifier.fillMaxWidth(),
            borderColor = stateColor.copy(alpha = 0.5f)
        ) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Engine State",
                        color = TextSecondary,
                        fontSize = 13.sp
                    )
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier
                                .size(10.dp)
                                .clip(CircleShape)
                                .background(stateColor)
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = flowkitStatus.state,
                            color = stateColor,
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }

                Text(
                    text = "Endpoint: ${flowkitStatus.endpoint} | Port: ${flowkitStatus.port} | WS: ${flowkitStatus.websocketPort}",
                    color = TextSecondary,
                    fontSize = 12.sp
                )
            }
        }

        // Action Buttons Row
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Button(
                onClick = { viewModel.controlFlowKitEngine("start") },
                modifier = Modifier.weight(1f),
                colors = ButtonDefaults.buttonColors(containerColor = NeonEmerald.copy(alpha = 0.3f)),
                shape = RoundedCornerShape(12.dp)
            ) {
                Text("Start", color = NeonEmerald, fontWeight = FontWeight.Bold)
            }

            Button(
                onClick = { viewModel.controlFlowKitEngine("restart") },
                modifier = Modifier.weight(1f),
                colors = ButtonDefaults.buttonColors(containerColor = NeonCyan.copy(alpha = 0.3f)),
                shape = RoundedCornerShape(12.dp)
            ) {
                Text("Restart", color = NeonCyan, fontWeight = FontWeight.Bold)
            }

            Button(
                onClick = { viewModel.controlFlowKitEngine("stop") },
                modifier = Modifier.weight(1f),
                colors = ButtonDefaults.buttonColors(containerColor = NeonRose.copy(alpha = 0.3f)),
                shape = RoundedCornerShape(12.dp)
            ) {
                Text("Stop", color = NeonRose, fontWeight = FontWeight.Bold)
            }
        }

        // Termux PRoot Engine Launcher
        GlassCard(modifier = Modifier.fillMaxWidth()) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(
                    text = "Termux PRoot Daemon Bridge",
                    color = TextPrimary,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "Dispatches start/restart instructions to Termux PRoot environment running on loopback.",
                    color = TextSecondary,
                    fontSize = 12.sp
                )
                OutlinedButton(
                    onClick = { TermuxBridge.startFlowKitEngine(context, "start") },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(10.dp)
                ) {
                    Text("Launch via Termux RUN_COMMAND", color = NeonCyan)
                }
            }
        }

        // Browser Extension Guide Card
        GlassCard(
            modifier = Modifier.fillMaxWidth(),
            borderColor = NeonAmber.copy(alpha = 0.3f)
        ) {
            Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(
                    text = "Google Flow Browser Compatibility",
                    color = NeonAmber,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "Standard Chrome Android does not support Manifest V3 Chrome Extensions. For automated cloud flow bridging, open flow.google.com in Kiwi Browser or Lemur Browser with the FlowKit extension loaded and connected to ws://127.0.0.1:9222.",
                    color = TextSecondary,
                    fontSize = 12.sp,
                    lineHeight = 16.sp
                )
            }
        }

        // Live Console / Logs Viewer
        GlassCard(modifier = Modifier.fillMaxWidth()) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "ENGINE CONSOLE LOGS",
                        color = TextPrimary,
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Bold
                    )
                    OutlinedButton(
                        onClick = { viewModel.refreshMediaCompany() },
                        shape = RoundedCornerShape(8.dp),
                        contentPadding = PaddingValues(horizontal = 8.dp, vertical = 2.dp)
                    ) {
                        Text("Refresh Logs", color = NeonCyan, fontSize = 11.sp)
                    }
                }

                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(180.dp)
                        .clip(RoundedCornerShape(8.dp))
                        .background(Color.Black.copy(alpha = 0.6f))
                        .padding(8.dp)
                        .verticalScroll(rememberScrollState())
                ) {
                    Text(
                        text = logs.ifBlank { "No active logs. FlowKit engine ready on port 8100." },
                        color = NeonEmerald,
                        fontSize = 11.sp,
                        fontFamily = FontFamily.Monospace,
                        lineHeight = 14.sp
                    )
                }
            }
        }
    }
}
