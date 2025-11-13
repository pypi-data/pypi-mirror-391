import {Card, Group, Stack, Text} from "@mantine/core";

import type {TrainingProtocol} from "../models/trainingProtocol.ts";

export const ProtocolProgress = ({protocol}: {protocol: TrainingProtocol}) => {
    return (
        <Card miw={600} mih={240} withBorder>
            <Card.Section bg="blue.2">
                <Group p={4} justify="space-between">
                    <Text fw={500}>Protocol Progress</Text>
                </Group>
            </Card.Section>
            {protocol ? <ProtocolProgressContent protocol={protocol}/> : null}
        </Card>
    );
}

const ProtocolProgressContent = ({protocol}: {protocol: TrainingProtocol}) => {
    return (
        <Stack>
        </Stack>
    )
}
