package com.ghdinteractivestudio.aioffice.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.ghdinteractivestudio.aioffice.ui.components.GlassCard
import com.ghdinteractivestudio.aioffice.ui.theme.*
import com.ghdinteractivestudio.aioffice.viewmodel.OfficeViewModel

@Composable
fun OrganizationalMemoryScreen(viewModel: OfficeViewModel) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = "ORGANIZATIONAL MEMORY",
            color = NeonCyan,
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold
        )
        Text(
            text = "Verified intelligence, market research, provenance, and corporate memory.",
            color = TextSecondary,
            fontSize = 12.sp
        )

        Spacer(modifier = Modifier.height(16.dp))

        val memories = listOf(
            Pair("Commercial Boundary Rule", "Provenance: Finance Director • Cost Invariant = $0.00 • No paid models allowed"),
            Pair("User ↔ AI CEO Governance Protocol", "Provenance: Governance Charter • Owner retains final authorization on external side-effects"),
            Pair("Glassmorphism 2.0 Design System", "Provenance: Creative Studio • Frosted translucent surfaces, deep graphite, neon cyan accents"),
            Pair("TikTok & Meta API Scopes", "Provenance: Technology Dept • PKCE S256 required, official container publishing endpoints verified")
        )

        LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp)) {
            items(memories.size) { index ->
                val (title, body) = memories[index]
                GlassCard(modifier = Modifier.fillMaxWidth()) {
                    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Text(title, color = TextPrimary, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                        Text(body, color = TextSecondary, fontSize = 12.sp, lineHeight = 16.sp)
                    }
                }
            }
        }
    }
}
