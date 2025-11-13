export type IConnectionData = import("../../utils/connectionData/IConnectionData.js").IConnectionData;
/**
 * @typedef {import('../../utils/connectionData/IConnectionData.js').IConnectionData} IConnectionData
 */
export class CommandSerializer {
    /**
     * Serializes the root command with connection data and optional runtime version.
     * @param {Promise<Command> | Command} rootCommand
     * @param {IConnectionData} connectionData
     * @param {number} runtimeVersion
     * @returns {Promise<Uint8Array> | Uint8Array}
     */
    serialize(rootCommand: Promise<Command> | Command, connectionData: IConnectionData, runtimeVersion?: number): Promise<Uint8Array> | Uint8Array;
    /**
     * Recursively serializes command payload.
     * @param {Command} command
     * @param {Array<Uint8Array>} buffers
     */
    serializeRecursively(command: Command, buffers: Array<Uint8Array>): void;
}
import { Command } from '../../utils/Command.js';
