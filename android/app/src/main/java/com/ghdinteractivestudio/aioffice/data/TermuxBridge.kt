package com.ghdinteractivestudio.aioffice.data

import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.widget.Toast

object TermuxBridge {

    private const val TERMUX_PACKAGE = "com.termux"
    private const val ACTION_RUN_COMMAND = "com.termux.RUN_COMMAND"
    private const val EXTRA_RUN_COMMAND_PATH = "com.termux.RUN_COMMAND_PATH"
    private const val EXTRA_RUN_COMMAND_ARGUMENTS = "com.termux.RUN_COMMAND_ARGUMENTS"
    private const val EXTRA_RUN_COMMAND_WORKDIR = "com.termux.RUN_COMMAND_WORKDIR"
    private const val EXTRA_RUN_COMMAND_BACKGROUND = "com.termux.RUN_COMMAND_BACKGROUND"
    private const val EXTRA_RUN_COMMAND_SESSION_ACTION = "com.termux.RUN_COMMAND_SESSION_ACTION"

    /**
     * Launch FlowKit daemon inside Termux PRoot environment via RUN_COMMAND intent,
     * with graceful fallback to opening Termux directly.
     */
    fun startFlowKitEngine(context: Context, action: String = "start") {
        try {
            val intent = Intent(ACTION_RUN_COMMAND).apply {
                component = ComponentName(TERMUX_PACKAGE, "com.termux.app.RunCommandService")
                putExtra(EXTRA_RUN_COMMAND_PATH, "/data/data/com.termux/files/usr/bin/proot-distro")
                putExtra(
                    EXTRA_RUN_COMMAND_ARGUMENTS,
                    arrayOf("login", "ubuntu", "--", "/bin/bash", "/root/ai-office/scripts/flowkit_service.sh", action)
                )
                putExtra(EXTRA_RUN_COMMAND_WORKDIR, "/data/data/com.termux/files/home")
                putExtra(EXTRA_RUN_COMMAND_BACKGROUND, true)
                putExtra(EXTRA_RUN_COMMAND_SESSION_ACTION, "0")
            }
            context.startService(intent)
            Toast.makeText(context, "FlowKit $action command dispatched to Termux PRoot", Toast.LENGTH_SHORT).show()
        } catch (e: Exception) {
            // Fallback: Open Termux application directly
            openTermuxFallback(context)
        }
    }

    /**
     * Fallback to opening Termux app if RUN_COMMAND service is restricted or unavailable.
     */
    fun openTermuxFallback(context: Context) {
        val launchIntent = context.packageManager.getLaunchIntentForPackage(TERMUX_PACKAGE)
        if (launchIntent != null) {
            launchIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            context.startActivity(launchIntent)
            Toast.makeText(context, "Opened Termux. Run: scripts/flowkit_service.sh start", Toast.LENGTH_LONG).show()
        } else {
            Toast.makeText(
                context,
                "Termux is not installed. Install Termux to run the FlowKit video engine locally.",
                Toast.LENGTH_LONG
            ).show()
        }
    }
}
