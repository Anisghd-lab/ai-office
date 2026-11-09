package com.ghdinteractivestudio.aioffice.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.ghdinteractivestudio.aioffice.ui.components.GlassCard
import com.ghdinteractivestudio.aioffice.ui.theme.*
import com.ghdinteractivestudio.aioffice.viewmodel.OfficeViewModel

@Composable
fun SocialAccountsScreen(viewModel: OfficeViewModel) {
    val accounts by viewModel.socialAccounts.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = "OFFICIAL SOCIAL ACCOUNTS",
            color = NeonCyan,
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold
        )
        Text(
            text = "PKCE OAuth connections for official platform publication.",
            color = TextSecondary,
            fontSize = 12.sp
        )

        Spacer(modifier = Modifier.height(16.dp))

        val platforms = listOf("tiktok", "facebook", "instagram")

        LazyColumn(verticalArrangement = Arrangement.spacedBy(14.dp)) {
            items(platforms.size) { index ->
                val plat = platforms[index]
                val item = accounts[plat]
                val isConnected = item?.status == "CONNECTED"

                GlassCard(
                    modifier = Modifier.fillMaxWidth(),
                    borderColor = if (isConnected) NeonEmerald.copy(alpha = 0.5f) else GlassBorder
                ) {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                text = plat.uppercase(),
                                color = TextPrimary,
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                text = item?.status ?: "DISCONNECTED",
                                color = if (isConnected) NeonEmerald else NeonAmber,
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }

                        Text(
                            text = if (isConnected) "Linked Account: ${item?.username ?: "Authenticated"}" else "No active OAuth session. PKCE authorization required.",
                            color = TextSecondary,
                            fontSize = 12.sp
                        )

                        Text(
                            text = "Capabilities: ${item?.capabilities?.joinToString() ?: "Official API Posting"}",
                            color = TextTertiary,
                            fontSize = 11.sp
                        )

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.End
                        ) {
                            if (!isConnected) {
                                Button(
                                    onClick = { /* Launch OAuth in browser / custom tab */ },
                                    colors = ButtonDefaults.buttonColors(containerColor = NeonCyan)
                                ) {
                                    Text("CONNECT ACCOUNT", color = DeepBlackBg, fontWeight = FontWeight.Bold, fontSize = 12.sp)
                                }
                            } else {
                                OutlinedButton(
                                    onClick = { /* Disconnect */ },
                                    colors = ButtonDefaults.outlinedButtonColors(contentColor = NeonRose)
                                ) {
                                    Text("DISCONNECT", fontSize = 12.sp)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
