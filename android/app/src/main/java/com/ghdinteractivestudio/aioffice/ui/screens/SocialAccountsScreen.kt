package com.ghdinteractivestudio.aioffice.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.ghdinteractivestudio.aioffice.data.SocialAccountStatus
import com.ghdinteractivestudio.aioffice.ui.components.GlassCard
import com.ghdinteractivestudio.aioffice.ui.theme.*
import com.ghdinteractivestudio.aioffice.viewmodel.OfficeViewModel

data class PlatformMeta(
    val key: String,
    val displayName: String,
    val category: String,
    val defaultCapabilities: List<String>
)

val SUPPORTED_PLATFORMS = listOf(
    PlatformMeta("google-1", "Google Account 1", "Primary Identity", listOf("Identity Verification", "Profile Read", "Zero-Cost Quota")),
    PlatformMeta("google-2", "Google Account 2", "Failover Quota", listOf("Identity Verification", "Independent Quota")),
    PlatformMeta("google-3", "Google Account 3", "Tertiary Quota", listOf("Identity Verification", "Failover Quota")),
    PlatformMeta("youtube", "YouTube Official Channel", "Video Broadcast", listOf("Channel Read", "Video Upload", "Shorts Publishing", "Analytics")),
    PlatformMeta("tiktok", "TikTok Creator Account", "Shorts & Video", listOf("Direct Video Post", "Creator Analytics")),
    PlatformMeta("instagram", "Instagram Professional", "Photo & Reels", listOf("Reels Publishing", "Photo Feed", "Insights Read")),
    PlatformMeta("facebook", "Facebook Official Page", "Social Broadcast", listOf("Page Feed Post", "Page Insights", "Engagement Read"))
)

@Composable
fun SocialAccountsScreen(viewModel: OfficeViewModel) {
    val context = LocalContext.current
    val accounts by viewModel.socialAccounts.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(
                    text = "CONNECTED ACCOUNTS",
                    color = NeonCyan,
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "One-tap PKCE OAuth integrations with live harmless read-only test verification.",
                    color = TextSecondary,
                    fontSize = 12.sp
                )
            }
            IconButton(onClick = { viewModel.refreshAll() }) {
                Text("🔄", fontSize = 18.sp)
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Platform Cards List
        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(14.dp),
            contentPadding = PaddingValues(bottom = 24.dp)
        ) {
            items(SUPPORTED_PLATFORMS) { meta ->
                val acc = accounts[meta.key]
                val opStatus = acc?.operationalStatus ?: "DISCONNECTED"
                val isOperational = opStatus == "API_OPERATIONAL"
                val isAuthorized = opStatus in listOf("ACCOUNT_AUTHORIZED", "PUBLISHING_READY", "API_OPERATIONAL")
                val isExpired = opStatus == "TOKEN_EXPIRED"
                val isError = opStatus == "ERROR"

                val borderColor = when {
                    isOperational -> NeonEmerald.copy(alpha = 0.7f)
                    isAuthorized -> NeonAmber.copy(alpha = 0.6f)
                    isExpired || isError -> NeonRose.copy(alpha = 0.7f)
                    else -> GlassBorder
                }

                val statusColor = when {
                    isOperational -> NeonEmerald
                    isAuthorized -> NeonAmber
                    isExpired || isError -> NeonRose
                    else -> TextSecondary
                }

                GlassCard(
                    modifier = Modifier.fillMaxWidth(),
                    borderColor = borderColor
                ) {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        // Title + Badges
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column {
                                Text(
                                    text = meta.displayName,
                                    color = TextPrimary,
                                    fontSize = 16.sp,
                                    fontWeight = FontWeight.Bold
                                )
                                Text(
                                    text = meta.category,
                                    color = TextTertiary,
                                    fontSize = 11.sp
                                )
                            }

                            // Status Pill
                            Box(
                                modifier = Modifier
                                    .clip(RoundedCornerShape(8.dp))
                                    .background(statusColor.copy(alpha = 0.15f))
                                    .border(1.dp, statusColor.copy(alpha = 0.5f), RoundedCornerShape(8.dp))
                                    .padding(horizontal = 8.dp, vertical = 4.dp)
                            ) {
                                Text(
                                    text = opStatus,
                                    color = statusColor,
                                    fontSize = 10.sp,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }

                        // Identity & Details
                        val accountLabel = acc?.username ?: acc?.accountId ?: "Not Connected"
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(text = "Account: ", color = TextSecondary, fontSize = 12.sp)
                            Text(
                                text = accountLabel,
                                color = if (isAuthorized) NeonCyan else TextPrimary,
                                fontSize = 12.sp,
                                fontWeight = FontWeight.SemiBold
                            )
                        }

                        // Capabilities Chips
                        val caps = if (!acc?.capabilities.isNullOrEmpty()) acc?.capabilities!! else meta.defaultCapabilities
                        Text(text = "Verified Capabilities:", color = TextSecondary, fontSize = 11.sp)
                        LazyRow(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                            items(caps) { cap ->
                                Box(
                                    modifier = Modifier
                                        .clip(RoundedCornerShape(6.dp))
                                        .background(GlassFillSubtle)
                                        .border(1.dp, GlassBorder, RoundedCornerShape(6.dp))
                                        .padding(horizontal = 6.dp, vertical = 2.dp)
                                    ) {
                                        Text(text = cap, color = TextPrimary, fontSize = 10.sp)
                                    }
                            }
                        }

                        // Scopes summary if authorized
                        if (!acc?.scopes.isNullOrEmpty()) {
                            Text(
                                text = "Scopes: ${acc?.scopes?.joinToString(", ")}",
                                color = TextTertiary,
                                fontSize = 10.sp,
                                maxLines = 2
                            )
                        }

                        Spacer(modifier = Modifier.height(4.dp))

                        // Action Buttons
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.End,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            if (!isAuthorized) {
                                OutlinedButton(
                                    onClick = { viewModel.simulateConnectPlatform(meta.key) },
                                    colors = ButtonDefaults.outlinedButtonColors(contentColor = NeonEmerald),
                                    modifier = Modifier.padding(end = 8.dp)
                                ) {
                                    Text("QUICK VERIFY", fontSize = 11.sp)
                                }
                                Button(
                                    onClick = { viewModel.connectPlatform(context, meta.key) },
                                    colors = ButtonDefaults.buttonColors(containerColor = NeonCyan)
                                ) {
                                    Text("CONNECT", color = DeepBlackBg, fontWeight = FontWeight.Bold, fontSize = 12.sp)
                                }
                            } else {
                                OutlinedButton(
                                    onClick = { viewModel.disconnectPlatform(meta.key) },
                                    colors = ButtonDefaults.outlinedButtonColors(contentColor = NeonRose),
                                    modifier = Modifier.padding(end = 6.dp)
                                ) {
                                    Text("DISCONNECT", fontSize = 11.sp)
                                }
                                if (isExpired || isError) {
                                    Button(
                                        onClick = { viewModel.reauthorizePlatform(context, meta.key) },
                                        colors = ButtonDefaults.buttonColors(containerColor = NeonAmber),
                                        modifier = Modifier.padding(end = 6.dp)
                                    ) {
                                        Text("REAUTHORIZE", color = DeepBlackBg, fontWeight = FontWeight.Bold, fontSize = 11.sp)
                                    }
                                }
                                Button(
                                    onClick = { viewModel.testPlatformConnection(meta.key) },
                                    colors = ButtonDefaults.buttonColors(containerColor = NeonCyan)
                                ) {
                                    Text("TEST API", color = DeepBlackBg, fontWeight = FontWeight.Bold, fontSize = 11.sp)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
