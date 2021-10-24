from mnist_training.src.main import main
import mnist_training.src.main


def test_main(mocker, minimal_dataloader, training_dependencies):
    mocker.patch(
        'mnist_training.src.main.create_dataloader',
        return_value=minimal_dataloader
    )

    mocker.patch(
        'mnist_training.src.main.create_training_dependencies',
        return_value=training_dependencies
    )

    mocker.patch.object(mnist_training.src.main, "EPOCHS", 1)

    main()